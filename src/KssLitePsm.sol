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

interface VatLike {
    function frob(bytes32, address, address, address, int256, int256) external;
    function hope(address) external;
    function ilks(bytes32) external view returns (uint256, uint256, uint256, uint256, uint256);
    function debt() external view returns (uint256);
    function Line() external view returns (uint256);
    function urns(bytes32, address) external view returns (uint256, uint256);
    function live() external view returns (uint256);
}

interface GemLike {
    function balanceOf(address) external view returns (uint256);
    function decimals() external view returns (uint8);
    function approve(address, uint256) external;
    function transfer(address, uint256) external;
    function transferFrom(address, address, uint256) external;
}

interface KusdJoinLike {
    function kusd() external view returns (address);
    function vat() external view returns (address);
    function exit(address, uint256) external;
    function join(address, uint256) external;
}

/**
 * @title A lightweight PSM implementation.
 * @notice Swaps Kusd for `gem` at a 1:1 exchange rate.
 * @notice Fees `tin` and `tout` might apply.
 * @dev `gem` balance is kept in `pocket` instead of this contract.
 * @dev A few assumptions are made:
 *      1. There are no other urns for the same `ilk`
 *      2. Stability fee is always zero for the `ilk`
 *      3. The `spot` price for gem is always 1 (`10**27`).
 *      4. The `spotter.par` (Kusd parity) is always 1 (`10**27`).
 *      5. This contract can freely transfer `gem` on behalf of `pocket`.
 */
contract KssLitePsm {
    /// @notice Special value for `tin` and/or `tout` to indicate swaps are halted.
    /// @dev Setting `tin` or `tout` to `type(uint256).max` will cause sell gem and buy gem functions respectively to revert.
    uint256 public constant HALTED = type(uint256).max;
    /// @notice Collateral type identifier.
    bytes32 public immutable ilk;
    /// @notice Maker Protocol core engine.
    VatLike public immutable vat;
    /// @notice Kusd adapter.
    KusdJoinLike public immutable kusdJoin;
    /// @notice Kusd token.
    GemLike public immutable kusd;
    /// @notice Gem to exchange with Kusd.
    GemLike public immutable gem;
    /// @notice Precision conversion factor for `gem`, since Kusd is expected to always have 18 decimals.
    uint256 public immutable to18ConversionFactor;
    /// @notice The ultimate holder of the gems.
    /// @dev This contract should be able to freely transfer `gem` on behalf of `pocket`.
    address public immutable pocket;

    /// @notice Addresses with admin access on this contract. `wards[usr]`.
    mapping(address => uint256) public wards;
    /// @notice Addresses with permission to swap with no fees. `bud[usr]`.
    mapping(address => uint256) public bud;
    /// @notice Maker Protocol balance sheet.
    address public vow;
    /// @notice Fee for selling gems.
    /// @dev `wad` precision. 1 * WAD means a 100% fee.
    uint256 public tin;
    /// @notice Fee for buying gems.
    /// @dev `wad` precision. 1 * WAD means a 100% fee.
    uint256 public tout;
    /// @notice Buffer for pre-minted Kusd.
    /// @dev `wad` precision.
    uint256 public buf;

    /// @dev `wad` precision.
    uint256 internal constant WAD = 10 ** 18;
    /// @dev `ray` precision for `vat` manipulation.
    uint256 internal constant RAY = 10 ** 27;
    /// @dev Workaround to explicitly revert with an arithmetic error.
    string internal constant ARITHMETIC_ERROR = string(abi.encodeWithSignature("Panic(uint256)", 0x11));

    /**
     * @notice `usr` was granted admin access.
     * @param usr The user address.
     */
    event Rely(address indexed usr);
    /**
     * @notice `usr` admin access was revoked.
     * @param usr The user address.
     */
    event Deny(address indexed usr);
    /**
     * @notice `usr` was granted permission to swap without any fees.
     * @param usr The user address.
     */
    event Kiss(address indexed usr);
    /**
     * @notice Permission revoked for `usr` to swap without any fees.
     * @param usr The user address.
     */
    event Diss(address indexed usr);
    /**
     * @notice A contract parameter was updated.
     * @param what The changed parameter name. ["vow"].
     * @param data The new value of the parameter.
     */
    event File(bytes32 indexed what, address data);
    /**
     * @notice A contract parameter was updated.
     * @param what The changed parameter name. ["tin", "tout", "buf"].
     * @param data The new value of the parameter.
     */
    event File(bytes32 indexed what, uint256 data);
    /**
     * @notice A user sold `gem` for Kusd.
     * @param owner The address receiving Kusd.
     * @param value The amount of `gem` sold. [`gem` precision].
     * @param fee The fee in Kusd paid by the user. [`wad`].
     */
    event SellGem(address indexed owner, uint256 value, uint256 fee);
    /**
     * @notice A user bought `gem` with Kusd.
     * @param owner The address receiving `gem`.
     * @param value The amount of `gem` bought. [`gem` precision].
     * @param fee The fee in Kusd paid by the user. [`wad`].
     */
    event BuyGem(address indexed owner, uint256 value, uint256 fee);
    /**
     * @notice The contract was filled with Kusd.
     * @param wad The amount of Kusd filled.
     */
    event Fill(uint256 wad);
    /**
     * @notice The contract was trimmed of excess Kusd.
     * @param wad The amount of Kusd trimmed.
     */
    event Trim(uint256 wad);
    /**
     * @notice Kusd accumulated as swap fees was added to the surplus buffer.
     * @param wad The amount of Kusd added.
     */
    event Chug(uint256 wad);

    modifier auth() {
        require(wards[msg.sender] == 1, "KssLitePsm/not-authorized");
        _;
    }

    modifier toll() {
        require(bud[msg.sender] == 1, "KssLitePsm/not-whitelisted");
        _;
    }

    /**
     * @param ilk_ The collateral type identifier.
     * @param gem_ The gem to exchange with Kusd.
     * @param kusdJoin_ The Kusd adapter.
     * @param pocket_ The ultimate holder of `gem`.
     */
    constructor(bytes32 ilk_, address gem_, address kusdJoin_, address pocket_) {
        ilk = ilk_;
        gem = GemLike(gem_);
        kusdJoin = KusdJoinLike(kusdJoin_);
        vat = VatLike(kusdJoin.vat());
        kusd = GemLike(kusdJoin.kusd());
        pocket = pocket_;

        to18ConversionFactor = 10 ** (18 - gem.decimals());

        kusd.approve(kusdJoin_, type(uint256).max);
        vat.hope(kusdJoin_);

        wards[msg.sender] = 1;
        emit Rely(msg.sender);
    }

    /*//////////////////////////////////
                    Math
    //////////////////////////////////*/

    ///@dev Safely converts `uint256` to `int256`. Reverts if it overflows.
    function _int256(uint256 x) internal pure returns (int256 y) {
        require((y = int256(x)) >= 0, ARITHMETIC_ERROR);
    }

    ///@dev Returns the min between `x` and `y`.
    function _min(uint256 x, uint256 y) internal pure returns (uint256 z) {
        return x < y ? x : y;
    }

    ///@dev Returns the max between `x` and `y`.
    function _max(uint256 x, uint256 y) internal pure returns (uint256 z) {
        return x > y ? x : y;
    }

    ///@dev Returns the difference between `x` and `y` if `x > y` or zero otherwise.
    function _subcap(uint256 x, uint256 y) internal pure returns (uint256 z) {
        unchecked {
            z = x > y ? x - y : 0;
        }
    }

    /*//////////////////////////////////
               Administration
    //////////////////////////////////*/

    /**
     * @notice Grants `usr` admin access to this contract.
     * @param usr The user address.
     */
    function rely(address usr) external auth {
        wards[usr] = 1;
        emit Rely(usr);
    }

    /**
     * @notice Revokes `usr` admin access from this contract.
     * @param usr The user address.
     */
    function deny(address usr) external auth {
        wards[usr] = 0;
        emit Deny(usr);
    }

    /**
     * @notice Grants `usr` permission to swap without any fees.
     * @param usr The user address.
     */
    function kiss(address usr) external auth {
        bud[usr] = 1;
        emit Kiss(usr);
    }

    /**
     * @notice Revokes `usr` permission to swap without any fees.
     * @param usr The user address.
     */
    function diss(address usr) external auth {
        bud[usr] = 0;
        emit Diss(usr);
    }

    /**
     * @notice Updates a contract parameter.
     * @param what The changed parameter name. ["vow"].
     * @param data The new value of the parameter.
     */
    function file(bytes32 what, address data) external auth {
        if (what == "vow") {
            vow = data;
        } else {
            revert("KssLitePsm/file-unrecognized-param");
        }

        emit File(what, data);
    }

    /**
     * @notice Updates a contract parameter.
     * @dev Swapping fees may not apply due to rounding errors for small swaps where
     *      `gemAmt < 10**gem.decimals() / tin` or
     *      `gemAmt < 10**gem.decimals() / tout`.
     * @dev Setting `tin` or `tout` to `HALTED` effectively disables selling and buying gems respectively.
     * @param what The changed parameter name. ["tin", "tout", "buf"].
     * @param data The new value of the parameter.
     */
    function file(bytes32 what, uint256 data) external auth {
        if (what == "tin") {
            require(data == HALTED || data <= WAD, "KssLitePsm/tin-out-of-range");
            tin = data;
        } else if (what == "tout") {
            require(data == HALTED || data <= WAD, "KssLitePsm/tout-out-of-range");
            tout = data;
        } else if (what == "buf") {
            buf = data;
        } else {
            revert("KssLitePsm/file-unrecognized-param");
        }

        emit File(what, data);
    }

    /*//////////////////////////////////
                  Swapping
    //////////////////////////////////*/

    /**
     * @notice Function that swaps `gem` into Kusd.
     * @dev Reverts if `tin` is set to `HALTED`.
     * @param usr The destination of the bought Kusd.
     * @param gemAmt The amount of gem to sell. [`gem` precision].
     * @return kusdOutWad The amount of Kusd bought.
     */
    function sellGem(address usr, uint256 gemAmt) external returns (uint256 kusdOutWad) {
        uint256 tin_ = tin;
        require(tin_ != HALTED, "KssLitePsm/sell-gem-halted");
        kusdOutWad = _sellGem(usr, gemAmt, tin_);
    }

    /**
     * @notice Function that swaps `gem` into Kusd without any fees.
     * @dev Only users whitelisted through `kiss()` can call this function.
     *      Reverts if `tin` is set to `HALTED`.
     * @param usr The destination of the bought Kusd.
     * @param gemAmt The amount of gem to sell. [`gem` precision].
     * @return kusdOutWad The amount of Kusd bought.
     */
    function sellGemNoFee(address usr, uint256 gemAmt) external toll returns (uint256 kusdOutWad) {
        require(tin != HALTED, "KssLitePsm/sell-gem-halted");
        kusdOutWad = _sellGem(usr, gemAmt, 0);
    }

    /**
     * @notice Internal function that implements the logic to swaps `gem` into Kusd.
     * @param usr The destination of the bought Kusd.
     * @param gemAmt The amount of gem to sell. [`gem` precision].
     * @param tin_ The fee rate applicable to the swap [`1 * WAD` = 100%].
     * @return kusdOutWad The amount of Kusd bought.
     */
    function _sellGem(address usr, uint256 gemAmt, uint256 tin_) internal returns (uint256 kusdOutWad) {
        kusdOutWad = gemAmt * to18ConversionFactor;
        uint256 fee;
        if (tin_ > 0) {
            fee = kusdOutWad * tin_ / WAD;
            // At this point, `tin_ <= 1 WAD`, so an underflow is not possible.
            unchecked {
                kusdOutWad -= fee;
            }
        }

        gem.transferFrom(msg.sender, pocket, gemAmt);
        // This can consume the whole balance including system fees not withdrawn.
        kusd.transfer(usr, kusdOutWad);

        emit SellGem(usr, gemAmt, fee);
    }

    /**
     * @notice Function that swaps Kusd into `gem`.
     * @dev Reverts if `tout` is set to `HALTED`.
     * @param usr The destination of the bought gems.
     * @param gemAmt The amount of gem to buy. [`gem` precision].
     * @return kusdInWad The amount of Kusd required to sell.
     */
    function buyGem(address usr, uint256 gemAmt) external returns (uint256 kusdInWad) {
        uint256 tout_ = tout;
        require(tout_ != HALTED, "KssLitePsm/buy-gem-halted");
        kusdInWad = _buyGem(usr, gemAmt, tout_);
    }

    /**
     * @notice Function that swaps Kusd into `gem` without any fees.
     * @dev Only users whitelisted through `kiss()` can call this function.
     *      Reverts if `tout` is set to `HALTED`.
     * @param usr The destination of the bought gems.
     * @param gemAmt The amount of gem to buy. [`gem` precision].
     * @return kusdInWad The amount of Kusd required to sell.
     */
    function buyGemNoFee(address usr, uint256 gemAmt) external toll returns (uint256 kusdInWad) {
        require(tout != HALTED, "KssLitePsm/buy-gem-halted");
        kusdInWad = _buyGem(usr, gemAmt, 0);
    }

    /**
     * @notice Internal function implementing the logic that swaps Kusd into `gem`.
     * @param usr The destination of the bought gems.
     * @param gemAmt The amount of gem to buy. [`gem` precision].
     * @param tout_ The fee rate applicable to the swap [`1 * WAD` = 100%].
     * @return kusdInWad The amount of Kusd required to sell.
     */
    function _buyGem(address usr, uint256 gemAmt, uint256 tout_) internal returns (uint256 kusdInWad) {
        kusdInWad = gemAmt * to18ConversionFactor;
        uint256 fee;
        if (tout_ > 0) {
            fee = kusdInWad * tout_ / WAD;
            kusdInWad += fee;
        }

        kusd.transferFrom(msg.sender, address(this), kusdInWad);
        gem.transferFrom(pocket, usr, gemAmt);

        emit BuyGem(usr, gemAmt, fee);
    }

    /*//////////////////////////////////
                Bookkeeping
    //////////////////////////////////*/

    /**
     * @notice Mints Kusd into this contract.
     * @dev Both `buf`, the local and global debt ceilings limit the actual minted amount.
     *      Notice that `gem` donations or extraneous debt repayments can also affect the amount.
     * @return wad The amount of Kusd minted.
     */
    function fill() external returns (uint256 wad) {
        wad = rush();
        require(wad > 0, "KssLitePsm/nothing-to-fill");

        // The `urn` for this contract in the `Vat` is expected to have "unlimited" `ink`.
        vat.frob(ilk, address(this), address(0), address(this), 0, _int256(wad));
        kusdJoin.exit(address(this), wad);

        emit Fill(wad);
    }

    /**
     * @notice Burns any excess of Kusd from this contract.
     * @dev The total outstanding debt can still be larger than the debt ceiling after `trim`.
     *      Additional `buyGem` calls will enable further `trim` calls.
     * @return wad The amount of Kusd burned.
     */
    function trim() external returns (uint256 wad) {
        wad = gush();
        require(wad > 0, "KssLitePsm/nothing-to-trim");

        kusdJoin.join(address(this), wad);
        // The `urn` for this contract in the `Vat` is expected to have "unlimited" `ink`.
        vat.frob(ilk, address(this), address(0), address(this), 0, -_int256(wad));

        emit Trim(wad);
    }

    /**
     * @notice Incorporates any outstanding accumulated fees into the surplus buffer.
     * @return wad The amount added to the surplus buffer.
     */
    function chug() external returns (uint256 wad) {
        address vow_ = vow;
        require(vow_ != address(0), "KssLitePsm/chug-missing-vow");

        wad = cut();
        require(wad > 0, "KssLitePsm/nothing-to-chug");

        kusdJoin.join(vow_, wad);

        emit Chug(wad);
    }

    /*//////////////////////////////////
                  Getters
    //////////////////////////////////*/

    /**
     * @notice Returns the missing Kusd that can be filled into this contract.
     * @return wad The amount of Kusd.
     */
    function rush() public view returns (uint256 wad) {
        (uint256 Art, uint256 rate,, uint256 line,) = vat.ilks(ilk);
        require(rate == RAY, "KssLitePsm/rate-not-RAY");
        uint256 tArt = gem.balanceOf(pocket) * to18ConversionFactor + buf;

        wad = _min(
            _min(
                // To avoid two extra SLOADs it assumes urn.art == ilk.Art.
                _subcap(tArt, Art),
                _subcap(line / RAY, Art)
            ),
            _subcap(vat.Line(), vat.debt()) / RAY
        );
    }

    /**
     * @notice Returns the excess Kusd that can be trimmed from this contract.
     * @return wad The amount of Kusd.
     */
    function gush() public view returns (uint256 wad) {
        (uint256 Art, uint256 rate,, uint256 line,) = vat.ilks(ilk);
        require(rate == RAY, "KssLitePsm/rate-not-RAY");
        uint256 tArt = gem.balanceOf(pocket) * to18ConversionFactor + buf;

        wad = _min(
            _max(
                // To avoid two extra SLOADs it assumes urn.art == ilk.Art.
                _subcap(Art, tArt),
                _subcap(Art, line / RAY)
            ),
            // Cannot burn more than the current balance.
            kusd.balanceOf(address(this))
        );
    }

    /**
     * @notice Returns the amount of swapping fees that can be chugged by this contract.
     * @dev To keep `_sellGem` gas usage low, it allows users to take pre-minted Kusd up to the whole balance, regardless
     *      if part of it consist of collected fees.
     *      If there is not enough balance, it will need to wait for new pre-minted Kusd to be generated or Kusd swapped
     *      back to complete the withdrawal of fees.
     * @return wad The amount of Kusd.
     */
    function cut() public view returns (uint256 wad) {
        (, uint256 art) = vat.urns(ilk, address(this));
        uint256 cash = kusd.balanceOf(address(this));

        wad = _min(cash, cash + gem.balanceOf(pocket) * to18ConversionFactor - art);
    }

    /*//////////////////////////////////
            Compatibility Layer
    //////////////////////////////////*/

    /**
     * @notice Returns the address of the LitePsm contract itself.
     * @dev LitePsm does not have an external gem join. All logic is handled internally.
     *      This function is required because there are some dependencies that assume every PSM has a gem join.
     * @return The address of this contract.
     */
    function gemJoin() external view returns (address) {
        return address(this);
    }

    /**
     * @notice Returns the number of decimals for `gem`.
     * @return The number of decimals for `gem`.
     */
    function dec() external view returns (uint256) {
        return gem.decimals();
    }

    /**
     * @notice Returns whether the contract is live or not.
     * @return Whether the contract is live or not.
     */
    function live() external view returns (uint256) {
        return vat.live();
    }
}
