// SPDX-FileCopyrightText: © 2023 Dai Foundation <www.daifoundation.org>
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


import {KssLitePsm} from "src/KssLitePsm.sol";
import {KssLitePsmInstance} from "./KssLitePsmInstance.sol";

struct KssLitePsmDeployParams {
    address deployer;
    address owner;
    bytes32 ilk;
    address gem;
    address kusdJoin;
    address pocket;
}

library KssLitePsmDeploy {
    function deploy(KssLitePsmDeployParams memory p) internal returns (KssLitePsmInstance memory r) {
        r.litePsm = address(new KssLitePsm(p.ilk, p.gem, p.kusdJoin, p.pocket));

        // ScriptTools.switchOwner(r.litePsm, p.deployer, p.owner);
        // Manually handle ownership transfer if needed, or assume deployer is owner initially
        if (p.owner != address(0) && p.owner != p.deployer) {
            KssLitePsm(r.litePsm).rely(p.owner);
            KssLitePsm(r.litePsm).deny(p.deployer);
        }
    }
}
