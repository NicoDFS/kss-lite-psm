// SPDX-FileCopyrightText: © 2023 Kusd Foundation <www.kusdfoundation.org>
// SPDX-License-Identifier: AGPL-3.0-or-later
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.
pragma solidity ^0.8.16;

import {Script} from "forge-std/Script.sol";
import {console} from "forge-std/console.sol";
import {stdJson} from "forge-std/StdJson.sol";
import {KssLitePsmDeploy, KssLitePsmDeployParams} from "src/deployment/KssLitePsmDeploy.sol";
import {KssLitePsmInstance} from "src/deployment/KssLitePsmInstance.sol";

interface VatLike {
    function rely(address) external;
    function file(bytes32, bytes32, uint256) external;
    function slip(bytes32, address, int256) external;
    function grab(bytes32, address, address, address, int256, int256) external;
}

interface PSMLike {
    function file(bytes32, address) external;
    function file(bytes32, uint256) external;
}

interface GemLike {
    function approve(address, uint256) external;
}

contract KssLitePsmDeployScript is Script {
    using stdJson for string;

    string constant NAME = "kss-lite-psm-deploy";
    
    // Constants
    uint256 constant RAY = 10 ** 27;
    uint256 constant WAD = 10 ** 18;
    
    // Environment variables
    string ilkStr;
    bytes32 ilk;
    address gem;
    address pocket;
    address kusdJoin;
    address owner;
    address vat;
    address vow;
    
    // Deployment result
    KssLitePsmInstance inst;
    
    // Configuration parameters (can be overridden via env)
    uint256 debtCeiling;  // line
    uint256 spotPrice;    // spot
    uint256 bufferSize;   // buf
    int256 collateralAmount; // ink
    bool skipVatConfig;   // Skip Vat configuration if already done

    function run() external {
        // Load configuration from environment
        loadConfig();
        
        console.log("=== PSM Deployment Configuration ===");
        console.log("ILK:", ilkStr);
        console.log("Gem:", gem);
        console.log("Pocket:", pocket);
        console.log("Owner:", owner);
        console.log("Vat:", vat);
        console.log("Vow:", vow);
        console.log("Skip Vat Config:", skipVatConfig);
        console.log("====================================");

        vm.startBroadcast();

        // 1. Deploy PSM
        console.log("\n1. Deploying PSM...");
        inst = KssLitePsmDeploy.deploy(
            KssLitePsmDeployParams({
                deployer: msg.sender,
                owner: owner,
                ilk: ilk,
                gem: gem,
                kusdJoin: kusdJoin,
                pocket: pocket
            })
        );
        console.log("PSM deployed at:", inst.litePsm);

        if (!skipVatConfig) {
            // 2. Configure Vat
            console.log("\n2. Configuring Vat...");
            configureVat();
        } else {
            console.log("\n2. Skipping Vat configuration (SKIP_VAT_CONFIG=true)");
        }

        // 3. Configure PSM
        console.log("\n3. Configuring PSM...");
        configurePSM();

        // 4. Approve pocket to spend gems (if pocket is not PSM itself)
        if (pocket != inst.litePsm && pocket == msg.sender) {
            console.log("\n4. Approving PSM to spend gems from pocket...");
            GemLike(gem).approve(inst.litePsm, type(uint256).max);
            console.log("Approval granted");
        } else {
            console.log("\n4. Skipping pocket approval (pocket is not deployer)");
        }

        vm.stopBroadcast();

        // Print deployment summary
        printSummary();
    }

    function loadConfig() internal {
        // Required parameters
        ilkStr = vm.envOr("FOUNDRY_ILK", string("USDC-A"));
        ilk = bytes32(bytes(ilkStr));
        gem = vm.envAddress("FOUNDRY_GEM");
        pocket = vm.envAddress("FOUNDRY_POCKET");
        kusdJoin = vm.envAddress("FOUNDRY_KUSD_JOIN");
        owner = vm.envAddress("FOUNDRY_OWNER");
        
        // Vat address (required for configuration)
        vat = vm.envOr("FOUNDRY_VAT", address(0x30e50aD44cd1890A6bf9F09Bf6b8AfE62a6a390D));
        vow = vm.envOr("FOUNDRY_VOW", address(0x12af8412fB89929E2C56b4b9ded7eaC06705d2DC));
        
        // Optional parameters with defaults
        debtCeiling = vm.envOr("FOUNDRY_DEBT_CEILING", uint256(100000000000000000000000000000000000000000000000000000)); // 1e53 (100M KUSD)
        spotPrice = vm.envOr("FOUNDRY_SPOT_PRICE", uint256(1000000000000000000000000000)); // 1 RAY
        bufferSize = vm.envOr("FOUNDRY_BUFFER_SIZE", uint256(100000000000000000000000)); // 100,000 KUSD
        collateralAmount = vm.envOr("FOUNDRY_COLLATERAL", int256(1000000000000000000000000000000)); // 1e30
        skipVatConfig = vm.envOr("SKIP_VAT_CONFIG", false);
    }

    function configureVat() internal {
        VatLike vatContract = VatLike(vat);
        
        // a. Authorize PSM on Vat
        console.log("  a. Authorizing PSM on Vat (rely)...");
        vatContract.rely(inst.litePsm);
        
        // b. Set debt ceiling for ilk
        console.log("  b. Setting debt ceiling...");
        vatContract.file(ilk, "line", debtCeiling);
        
        // c. Add collateral (gem) to PSM
        console.log("  c. Adding collateral to PSM (slip)...");
        vatContract.slip(ilk, inst.litePsm, collateralAmount);
        
        // d. Convert gem to ink (collateral)
        console.log("  d. Converting gem to ink (grab)...");
        vatContract.grab(ilk, inst.litePsm, inst.litePsm, inst.litePsm, collateralAmount, 0);
        
        // e. Set spot price
        console.log("  e. Setting spot price...");
        vatContract.file(ilk, "spot", spotPrice);
        
        console.log("Vat configuration complete");
    }

    function configurePSM() internal {
        PSMLike psm = PSMLike(inst.litePsm);
        
        // a. Set Vow address
        console.log("  a. Setting Vow address...");
        psm.file("vow", vow);
        
        // b. Set buffer size
        console.log("  b. Setting buffer size...");
        psm.file("buf", bufferSize);
        
        console.log("PSM configuration complete");
    }

    function printSummary() internal view {
        console.log("\n=== Deployment Summary ===");
        console.log("PSM Address:", inst.litePsm);
        console.log("ILK:", ilkStr);
        console.log("Gem:", gem);
        console.log("Pocket:", pocket);
        console.log("Owner:", owner);
        console.log("\nVat Configuration:");
        console.log("  Debt Ceiling:", debtCeiling);
        console.log("  Spot Price:", spotPrice);
        console.log("  Collateral:", uint256(collateralAmount));
        console.log("\nPSM Configuration:");
        console.log("  Vow:", vow);
        console.log("  Buffer:", bufferSize);
        console.log("==========================");
        console.log("\nNext steps:");
        console.log("1. Call fill() to mint KUSD into PSM");
        console.log("2. Test swap: sellGem(address, uint256)");
        console.log("3. Configure PSM keeper");
    }
}
