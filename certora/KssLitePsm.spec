// KssLitePsm.spec

using Vat as vat;
using KusdJoin as kusdJoin;
using Kusd as kusd;
using GemMock as gem;

methods {
    function ilk() external returns (bytes32) envfree;
    function to18ConversionFactor() external returns (uint256) envfree;
    function pocket() external returns (address) envfree;
    function wards(address) external returns (uint256) envfree;
    function bud(address) external returns (uint256) envfree;
    function vow() external returns (address) envfree;
    function tin() external returns (uint256) envfree;
    function tout() external returns (uint256) envfree;
    function buf() external returns (uint256) envfree;
    function rush() external returns (uint256) envfree;
    function gush() external returns (uint256) envfree;
    function cut() external returns (uint256) envfree;
    function HALTED() external returns (uint256) envfree;
    function vat.live() external returns (uint256) envfree;
    function vat.can(address, address) external returns (uint256) envfree;
    function vat.kusd(address) external returns (uint256) envfree;
    function vat.debt() external returns (uint256) envfree;
    function vat.Line() external returns (uint256) envfree;
    function vat.ilks(bytes32) external returns (uint256, uint256, uint256, uint256, uint256) envfree;
    function vat.urns(bytes32, address) external returns (uint256, uint256) envfree;
    function kusdJoin.live() external returns (uint256) envfree;
    function kusd.wards(address) external returns (uint256) envfree;
    function kusd.totalSupply() external returns (uint256) envfree;
    function kusd.balanceOf(address) external returns (uint256) envfree;
    function kusd.allowance(address, address) external returns (uint256) envfree;
    function gem.totalSupply() external returns (uint256) envfree;
    function gem.balanceOf(address) external returns (uint256) envfree;
    function gem.allowance(address, address) external returns (uint256) envfree;
}

definition WAD() returns mathint = 10^18;
definition RAY() returns mathint = 10^27;
definition max_int256() returns mathint = 2^255 - 1;
definition min(mathint x, mathint y) returns mathint = x < y ? x : y;
definition max(mathint x, mathint y) returns mathint = x > y ? x : y;
definition subCap(mathint x, mathint y) returns mathint = x > y ? x - y : 0;

// Verify that each storage layout is only modified in the corresponding functions
rule storageAffected(method f) {
    env e;

    address anyAddr;

    mathint wardsBefore = wards(anyAddr);
    mathint budBefore = bud(anyAddr);
    address vowBefore = vow();
    mathint tinBefore = tin();
    mathint toutBefore = tout();
    mathint bufBefore = buf();

    calldataarg args;
    f(e, args);

    mathint wardsAfter = wards(anyAddr);
    mathint budAfter = bud(anyAddr);
    address vowAfter = vow();
    mathint tinAfter = tin();
    mathint toutAfter = tout();
    mathint bufAfter = buf();

    assert wardsAfter != wardsBefore => f.selector == sig:rely(address).selector || f.selector == sig:deny(address).selector, "wards[x] changed in an unexpected function";
    assert budAfter != budBefore => f.selector == sig:kiss(address).selector || f.selector == sig:diss(address).selector, "bud[x] changed in an unexpected function";
    assert vowAfter != vowBefore => f.selector == sig:file(bytes32, address).selector, "vow changed in an unexpected function";
    assert tinAfter != tinBefore => f.selector == sig:file(bytes32, uint256).selector, "tin changed in an unexpected function";
    assert toutAfter != toutBefore => f.selector == sig:file(bytes32, uint256).selector, "tout changed in an unexpected function";
    assert bufAfter != bufBefore => f.selector == sig:file(bytes32, uint256).selector, "buf changed in an unexpected function";
}

// Verify correct storage changes for non reverting rely
rule rely(address usr) {
    env e;

    address otherAddr;
    require otherAddr != usr;

    mathint wardsOtherBefore = wards(otherAddr);

    rely(e, usr);

    mathint wardsUsrAfter = wards(usr);
    mathint wardsOtherAfter = wards(otherAddr);

    assert wardsUsrAfter == 1, "rely did not set wards[usr]";
    assert wardsOtherAfter == wardsOtherBefore, "rely did not keep unchanged the rest of wards[x]";
}

// Verify revert rules on rely
rule rely_revert(address usr) {
    env e;

    mathint warkssender = wards(e.msg.sender);

    rely@withrevert(e, usr);

    bool revert1 = e.msg.value > 0;
    bool revert2 = warkssender != 1;

    assert lastReverted <=> revert1 || revert2, "Revert rules failed";
}

// Verify correct storage changes for non reverting deny
rule deny(address usr) {
    env e;

    address otherAddr;
    require otherAddr != usr;

    mathint wardsOtherBefore = wards(otherAddr);

    deny(e, usr);

    mathint wardsUsrAfter = wards(usr);
    mathint wardsOtherAfter = wards(otherAddr);

    assert wardsUsrAfter == 0, "deny did not set wards[usr]";
    assert wardsOtherAfter == wardsOtherBefore, "deny did not keep unchanged the rest of wards[x]";
}

// Verify revert rules on deny
rule deny_revert(address usr) {
    env e;

    mathint warkssender = wards(e.msg.sender);

    deny@withrevert(e, usr);

    bool revert1 = e.msg.value > 0;
    bool revert2 = warkssender != 1;

    assert lastReverted <=> revert1 || revert2, "Revert rules failed";
}

// Verify correct storage changes for non reverting kiss
rule kiss(address usr) {
    env e;

    address otherAddr;
    require otherAddr != usr;

    mathint budOtherBefore = bud(otherAddr);

    kiss(e, usr);

    mathint budUsrAfter = bud(usr);
    mathint budOtherAfter = bud(otherAddr);

    assert budUsrAfter == 1, "kiss did not set bud[usr]";
    assert budOtherAfter == budOtherBefore, "kiss did not keep unchanged the rest of bud[x]";
}

// Verify revert rules on kiss
rule kiss_revert(address usr) {
    env e;

    mathint warkssender = wards(e.msg.sender);

    kiss@withrevert(e, usr);

    bool revert1 = e.msg.value > 0;
    bool revert2 = warkssender != 1;

    assert lastReverted <=> revert1 || revert2, "Revert rules failed";
}

// Verify correct storage changes for non reverting diss
rule diss(address usr) {
    env e;

    address otherAddr;
    require otherAddr != usr;

    mathint budOtherBefore = bud(otherAddr);

    diss(e, usr);

    mathint budUsrAfter = bud(usr);
    mathint budOtherAfter = bud(otherAddr);

    assert budUsrAfter == 0, "diss did not set bud[usr]";
    assert budOtherAfter == budOtherBefore, "diss did not keep unchanged the rest of bud[x]";
}

// Verify revert rules on diss
rule diss_revert(address usr) {
    env e;

    mathint warkssender = wards(e.msg.sender);

    diss@withrevert(e, usr);

    bool revert1 = e.msg.value > 0;
    bool revert2 = warkssender != 1;

    assert lastReverted <=> revert1 || revert2, "Revert rules failed";
}

// Verify correct storage changes for non reverting file
rule file_address(bytes32 what, address data) {
    env e;

    file(e, what, data);

    address vowAfter = vow();

    assert vowAfter == data, "file did not set vow";
}

// Verify revert rules on file
rule file_address_revert(bytes32 what, address data) {
    env e;

    mathint warkssender = wards(e.msg.sender);

    file@withrevert(e, what, data);

    bool revert1 = e.msg.value > 0;
    bool revert2 = warkssender != 1;
    bool revert3 = what != to_bytes32(0x766f770000000000000000000000000000000000000000000000000000000000);

    assert lastReverted <=> revert1 || revert2 || revert3, "Revert rules failed";
}

// Verify correct storage changes for non reverting file
rule file_uint256(bytes32 what, uint256 data) {
    env e;

    mathint tinBefore = tin();
    mathint toutBefore = tout();
    mathint bufBefore = buf();

    file(e, what, data);

    mathint tinAfter = tin();
    mathint toutAfter = tout();
    mathint bufAfter = buf();

    assert what == to_bytes32(0x74696e0000000000000000000000000000000000000000000000000000000000)
           => tinAfter == to_mathint(data), "file did not set tin";
    assert what != to_bytes32(0x74696e0000000000000000000000000000000000000000000000000000000000)
           => tinAfter == tinBefore, "file did not keep unchanged tin";
    assert what == to_bytes32(0x746f757400000000000000000000000000000000000000000000000000000000)
           => toutAfter == to_mathint(data), "file did not set tout";
    assert what != to_bytes32(0x746f757400000000000000000000000000000000000000000000000000000000)
           => toutAfter == toutBefore, "file did not keep unchanged tout";
    assert what == to_bytes32(0x6275660000000000000000000000000000000000000000000000000000000000)
           => bufAfter == to_mathint(data), "file did not set buf";
    assert what != to_bytes32(0x6275660000000000000000000000000000000000000000000000000000000000)
           => bufAfter == bufBefore, "file did not keep unchanged buf";
}

// Verify revert rules on file
rule file_uint256_revert(bytes32 what, uint256 data) {
    env e;

    mathint warkssender = wards(e.msg.sender);

    file@withrevert(e, what, data);

    bool revert1 = e.msg.value > 0;
    bool revert2 = warkssender != 1;
    bool revert3 = what != to_bytes32(0x74696e0000000000000000000000000000000000000000000000000000000000) &&
                   what != to_bytes32(0x746f757400000000000000000000000000000000000000000000000000000000) &&
                   what != to_bytes32(0x6275660000000000000000000000000000000000000000000000000000000000);
    bool revert4 = (what == to_bytes32(0x74696e0000000000000000000000000000000000000000000000000000000000) ||
                   what == to_bytes32(0x746f757400000000000000000000000000000000000000000000000000000000)) &&
                   to_mathint(data) > WAD() &&
                   to_mathint(data) != max_uint256;

    assert lastReverted <=> revert1 || revert2 || revert3 ||
                            revert4, "Revert rules failed";
}

// Verify correct storage changes for non reverting sellGem
rule sellGem(address usr, uint256 gemAmt) {
    env e;

    mathint tin = tin();
    require tin <= WAD();

    address pocket = pocket();
    require pocket != e.msg.sender;
    mathint to18ConversionFactor = to18ConversionFactor();

    mathint kusdBalanceOfUsrBefore = kusd.balanceOf(usr);
    mathint kusdBalanceOfPsmBefore = kusd.balanceOf(currentContract);
    mathint gemBalanceOfSenderBefore = gem.balanceOf(e.msg.sender);
    mathint gemBalanceOfPocketBefore = gem.balanceOf(pocket);
    require gemBalanceOfSenderBefore + gemBalanceOfPocketBefore <= to_mathint(gem.totalSupply());

    mathint gemAmtWad = gemAmt * to18ConversionFactor;
    mathint calcKusdOutWad = gemAmtWad - gemAmtWad * tin / WAD();

    mathint kusdOutWad = sellGem(e, usr, gemAmt);

    mathint kusdBalanceOfUsrAfter = kusd.balanceOf(usr);
    mathint kusdBalanceOfPsmAfter = kusd.balanceOf(currentContract);
    mathint gemBalanceOfSenderAfter = gem.balanceOf(e.msg.sender);
    mathint gemBalanceOfPocketAfter = gem.balanceOf(pocket);

    assert kusdOutWad == calcKusdOutWad, "sellGem did not return the expected kusdOutWad";
    assert gemBalanceOfSenderAfter == gemBalanceOfSenderBefore - gemAmt, "sellGem did not decrease gem.balanceOf(sender) by gemAmt";
    assert gemBalanceOfPocketAfter == gemBalanceOfPocketBefore + gemAmt, "sellGem did not increase gem.balanceOf(pocket) by gemAmt";
    assert usr != currentContract => kusdBalanceOfUsrAfter == kusdBalanceOfUsrBefore + kusdOutWad, "sellGem did not increase kusd.balanceOf(usr) by kusdOutWad";
    assert usr != currentContract => kusdBalanceOfPsmAfter == kusdBalanceOfPsmBefore - kusdOutWad, "sellGem did not decrease kusd.balanceOf(psm) by kusdOutWad";
    assert usr == currentContract => kusdBalanceOfUsrAfter == kusdBalanceOfUsrBefore, "sellGem did not keep the same kusd.balanceOf(usr/psm)";
}

// Verify revert rules on sellGem
rule sellGem_revert(address usr, uint256 gemAmt) {
    env e;

    require e.msg.sender != currentContract;

    mathint tin = tin();
    require tin <= WAD() || tin == max_uint256;

    mathint to18ConversionFactor = to18ConversionFactor();

    mathint kusdBalanceOfPsm = kusd.balanceOf(currentContract);
    require kusdBalanceOfPsm + kusd.balanceOf(usr) <= to_mathint(kusd.totalSupply());
    mathint gemAllowanceSenderPsm = gem.allowance(e.msg.sender, currentContract);
    mathint gemBalanceOfSender = gem.balanceOf(e.msg.sender);
    require gemBalanceOfSender + gem.balanceOf(pocket()) <= to_mathint(gem.totalSupply());

    mathint gemAmtWad = gemAmt * to18ConversionFactor;
    mathint kusdOutWad = gemAmtWad - gemAmtWad * tin / WAD();

    sellGem@withrevert(e, usr, gemAmt);

    bool revert1 = e.msg.value > 0;
    bool revert2 = gemAmtWad > max_uint256;
    bool revert3 = gemAmtWad * tin > max_uint256;
    bool revert4 = gemAllowanceSenderPsm < to_mathint(gemAmt);
    bool revert5 = gemBalanceOfSender < to_mathint(gemAmt);
    bool revert6 = kusdBalanceOfPsm < kusdOutWad;
    bool revert7 = tin == max_uint256;

    assert lastReverted <=> revert1 || revert2 || revert3 ||
                            revert4 || revert5 || revert6 ||
                            revert7, "Revert rules failed";
}

// Verify correct storage changes for non reverting sellGemNoFee
rule sellGemNoFee(address usr, uint256 gemAmt) {
    env e;

    address pocket = pocket();
    require pocket != e.msg.sender;
    mathint to18ConversionFactor = to18ConversionFactor();

    bytes32 ilk = ilk();

    mathint a; mathint vatUrnPsmArtBefore;
    a, vatUrnPsmArtBefore = vat.urns(ilk, currentContract);

    mathint kusdBalanceOfUsrBefore = kusd.balanceOf(usr);
    mathint kusdBalanceOfPsmBefore = kusd.balanceOf(currentContract);
    mathint gemBalanceOfSenderBefore = gem.balanceOf(e.msg.sender);
    mathint gemBalanceOfPocketBefore = gem.balanceOf(pocket);
    require gemBalanceOfSenderBefore + gemBalanceOfPocketBefore <= to_mathint(gem.totalSupply());

    mathint maxCutBefore = kusdBalanceOfPsmBefore + gemBalanceOfPocketBefore * to18ConversionFactor - vatUrnPsmArtBefore;

    mathint calcKusdOutWad = gemAmt * to18ConversionFactor;

    mathint kusdOutWad = sellGemNoFee(e, usr, gemAmt);

    mathint vatUrnPsmArtAfter;
    a, vatUrnPsmArtAfter = vat.urns(ilk, currentContract);

    mathint kusdBalanceOfUsrAfter = kusd.balanceOf(usr);
    mathint kusdBalanceOfPsmAfter = kusd.balanceOf(currentContract);
    mathint gemBalanceOfSenderAfter = gem.balanceOf(e.msg.sender);
    mathint gemBalanceOfPocketAfter = gem.balanceOf(pocket);

    mathint maxCutAfter = kusdBalanceOfPsmAfter + gemBalanceOfPocketAfter * to18ConversionFactor - vatUrnPsmArtAfter;

    assert kusdOutWad == calcKusdOutWad, "sellGemNoFee did not return the expected kusdOutWad";
    assert gemBalanceOfSenderAfter == gemBalanceOfSenderBefore - gemAmt, "sellGemNoFee did not decrease gem.balanceOf(sender) by gemAmt";
    assert gemBalanceOfPocketAfter == gemBalanceOfPocketBefore + gemAmt, "sellGemNoFee did not increase gem.balanceOf(pocket) by gemAmt";
    assert usr != currentContract => kusdBalanceOfUsrAfter == kusdBalanceOfUsrBefore + kusdOutWad, "sellGemNoFee did not increase kusd.balanceOf(usr) by kusdOutWad";
    assert usr != currentContract => kusdBalanceOfPsmAfter == kusdBalanceOfPsmBefore - kusdOutWad, "sellGemNoFee did not decrease kusd.balanceOf(psm) by kusdOutWad";
    assert usr == currentContract => kusdBalanceOfUsrAfter == kusdBalanceOfUsrBefore, "sellGemNoFee did not keep the same kusd.balanceOf(usr/psm)";
    assert usr != currentContract => maxCutAfter == maxCutBefore, "sellGemNoFee did not keep unchanged maxCut";
    assert usr == currentContract => maxCutAfter == maxCutBefore + kusdOutWad, "sellGemNoFee did not increase maxCut by kusdOutWad";
}

// Verify revert rules on sellGemNoFee
rule sellGemNoFee_revert(address usr, uint256 gemAmt) {
    env e;

    require e.msg.sender != currentContract;

    mathint budSender = bud(e.msg.sender);
    mathint tin = tin();
    mathint to18ConversionFactor = to18ConversionFactor();

    mathint kusdBalanceOfPsm = kusd.balanceOf(currentContract);
    require kusdBalanceOfPsm + kusd.balanceOf(usr) <= to_mathint(kusd.totalSupply());
    mathint gemAllowanceSenderPsm = gem.allowance(e.msg.sender, currentContract);
    mathint gemBalanceOfSender = gem.balanceOf(e.msg.sender);
    require gemBalanceOfSender + gem.balanceOf(pocket()) <= to_mathint(gem.totalSupply());

    mathint kusdOutWad = gemAmt * to18ConversionFactor;

    sellGemNoFee@withrevert(e, usr, gemAmt);

    bool revert1 = e.msg.value > 0;
    bool revert2 = budSender != 1;
    bool revert3 = kusdOutWad > max_uint256;
    bool revert4 = gemAllowanceSenderPsm < to_mathint(gemAmt);
    bool revert5 = gemBalanceOfSender < to_mathint(gemAmt);
    bool revert6 = kusdBalanceOfPsm < kusdOutWad;
    bool revert7 = tin == max_uint256;

    assert lastReverted <=> revert1 || revert2 || revert3 ||
                            revert4 || revert5 || revert6 ||
                            revert7, "Revert rules failed";
}

// Verify correct storage changes for non reverting buyGem
rule buyGem(address usr, uint256 gemAmt) {
    env e;

    require e.msg.sender != currentContract;

    mathint tout = tout();
    require tout <= WAD();

    address pocket = pocket();
    mathint to18ConversionFactor = to18ConversionFactor();

    mathint kusdBalanceOfSenderBefore = kusd.balanceOf(e.msg.sender);
    mathint kusdBalanceOfPsmBefore = kusd.balanceOf(currentContract);
    mathint gemBalanceOfUsrBefore = gem.balanceOf(usr);
    mathint gemBalanceOfPocketBefore = gem.balanceOf(pocket);
    require gemBalanceOfUsrBefore + gemBalanceOfPocketBefore <= to_mathint(gem.totalSupply());

    mathint gemAmtWad = gemAmt * to18ConversionFactor;
    mathint calcKusdInWad = gemAmtWad + gemAmtWad * tout / WAD();

    mathint kusdInWad = buyGem(e, usr, gemAmt);

    mathint kusdBalanceOfSenderAfter = kusd.balanceOf(e.msg.sender);
    mathint kusdBalanceOfPsmAfter = kusd.balanceOf(currentContract);
    mathint gemBalanceOfUsrAfter = gem.balanceOf(usr);
    mathint gemBalanceOfPocketAfter = gem.balanceOf(pocket);

    assert kusdInWad == calcKusdInWad, "buyGem did not return the expected kusdInWad";
    assert kusdBalanceOfSenderAfter == kusdBalanceOfSenderBefore - kusdInWad, "buyGem did not decrease kusd.balanceOf(sender) by kusdInWad";
    assert kusdBalanceOfPsmAfter == kusdBalanceOfPsmBefore + kusdInWad, "buyGem did not increase kusd.balanceOf(psm) by kusdInWad";
    assert usr != pocket => gemBalanceOfUsrAfter == gemBalanceOfUsrBefore + gemAmt, "buyGem did not increase gem.balanceOf(usr) by gemAmt";
    assert usr != pocket => gemBalanceOfPocketAfter == gemBalanceOfPocketBefore - gemAmt, "buyGem did not decrease gem.balanceOf(pocket) by gemAmt";
    assert usr == pocket => gemBalanceOfUsrAfter == gemBalanceOfUsrBefore, "buyGem did not keep unchanged gem.balanceOf(usr/pocket)";
}

// Verify revert rules on buyGem
rule buyGem_revert(address usr, uint256 gemAmt) {
    env e;

    require e.msg.sender != currentContract;

    mathint tout = tout();
    require tout <= WAD() || tout == max_uint256;

    mathint to18ConversionFactor = to18ConversionFactor();

    address pocket = pocket();
    require pocket != currentContract;

    mathint kusdBalanceOfSender = kusd.balanceOf(e.msg.sender);
    require kusdBalanceOfSender + kusd.balanceOf(currentContract) <= to_mathint(kusd.totalSupply());
    mathint kusdAllowanceSenderPsm = kusd.allowance(e.msg.sender, currentContract);
    mathint gemAllowancePocketPsm = gem.allowance(pocket, currentContract);
    mathint gemBalanceOfPocket = gem.balanceOf(pocket);
    require gemBalanceOfPocket + gem.balanceOf(usr) <= to_mathint(gem.totalSupply());

    mathint gemAmtWad = gemAmt * to18ConversionFactor;
    mathint kusdInWad = gemAmtWad + gemAmtWad * tout / WAD();

    buyGem@withrevert(e, usr, gemAmt);

    bool revert1 = e.msg.value > 0;
    bool revert2 = gemAmtWad > max_uint256;
    bool revert3 = gemAmtWad * tout > max_uint256;
    bool revert4 = kusdAllowanceSenderPsm < kusdInWad;
    bool revert5 = kusdBalanceOfSender < kusdInWad;
    bool revert6 = gemAllowancePocketPsm < to_mathint(gemAmt);
    bool revert7 = gemBalanceOfPocket < to_mathint(gemAmt);
    bool revert8 = tout == max_uint256;

    assert lastReverted <=> revert1 || revert2 || revert3 ||
                            revert4 || revert5 || revert6 ||
                            revert7 || revert8, "Revert rules failed";
}

// Verify correct storage changes for non reverting buyGemNoFee
rule buyGemNoFee(address usr, uint256 gemAmt) {
    env e;

    require e.msg.sender != currentContract;

    address pocket = pocket();
    mathint to18ConversionFactor = to18ConversionFactor();

    bytes32 ilk = ilk();

    mathint a; mathint vatUrnPsmArtBefore;
    a, vatUrnPsmArtBefore = vat.urns(ilk, currentContract);

    mathint kusdBalanceOfSenderBefore = kusd.balanceOf(e.msg.sender);
    mathint kusdBalanceOfPsmBefore = kusd.balanceOf(currentContract);
    mathint gemBalanceOfUsrBefore = gem.balanceOf(usr);
    mathint gemBalanceOfPocketBefore = gem.balanceOf(pocket);
    require gemBalanceOfUsrBefore + gemBalanceOfPocketBefore <= to_mathint(gem.totalSupply());

    mathint maxCutBefore = kusdBalanceOfPsmBefore + gemBalanceOfPocketBefore * to18ConversionFactor - vatUrnPsmArtBefore;

    mathint calcKusdInWad = gemAmt * to18ConversionFactor;

    mathint kusdInWad = buyGemNoFee(e, usr, gemAmt);

    mathint vatUrnPsmArtAfter;
    a, vatUrnPsmArtAfter = vat.urns(ilk, currentContract);

    mathint kusdBalanceOfSenderAfter = kusd.balanceOf(e.msg.sender);
    mathint kusdBalanceOfPsmAfter = kusd.balanceOf(currentContract);
    mathint gemBalanceOfUsrAfter = gem.balanceOf(usr);
    mathint gemBalanceOfPocketAfter = gem.balanceOf(pocket);

    mathint maxCutAfter = kusdBalanceOfPsmAfter + gemBalanceOfPocketAfter * to18ConversionFactor - vatUrnPsmArtAfter;

    assert kusdInWad == calcKusdInWad, "buyGemNoFee did not return the expected kusdInWad";
    assert kusdBalanceOfSenderAfter == kusdBalanceOfSenderBefore - kusdInWad, "buyGemNoFee did not decrease kusd.balanceOf(sender) by kusdInWad";
    assert kusdBalanceOfPsmAfter == kusdBalanceOfPsmBefore + kusdInWad, "buyGemNoFee did not increase kusd.balanceOf(psm) by kusdInWad";
    assert usr != pocket => gemBalanceOfUsrAfter == gemBalanceOfUsrBefore + gemAmt, "buyGemNoFee did not increase gem.balanceOf(usr) by gemAmt";
    assert usr != pocket => gemBalanceOfPocketAfter == gemBalanceOfPocketBefore - gemAmt, "buyGemNoFee did not decrease gem.balanceOf(pocket) by gemAmt";
    assert usr == pocket => gemBalanceOfUsrAfter == gemBalanceOfUsrBefore, "buyGemNoFee did not keep unchanged gem.balanceOf(usr/pocket)";
    assert usr != pocket => maxCutAfter == maxCutBefore, "buyGemNoFee did not keep unchanged maxCut";
    assert usr == pocket => maxCutAfter == maxCutBefore + kusdInWad, "buyGemNoFee did not increase maxCut by kusdInWad";
}

// Verify revert rules on buyGemNoFee
rule buyGemNoFee_revert(address usr, uint256 gemAmt) {
    env e;

    require e.msg.sender != currentContract;

    mathint to18ConversionFactor = to18ConversionFactor();
    mathint tout = tout();
    mathint budSender = bud(e.msg.sender);

    address pocket = pocket();
    require pocket != currentContract;

    mathint kusdBalanceOfSender = kusd.balanceOf(e.msg.sender);
    require kusdBalanceOfSender + kusd.balanceOf(currentContract) <= to_mathint(kusd.totalSupply());
    mathint kusdAllowanceSenderPsm = kusd.allowance(e.msg.sender, currentContract);
    mathint gemAllowancePocketPsm = gem.allowance(pocket, currentContract);
    mathint gemBalanceOfPocket = gem.balanceOf(pocket);
    require gemBalanceOfPocket + gem.balanceOf(usr) <= to_mathint(gem.totalSupply());

    mathint kusdInWad = gemAmt * to18ConversionFactor;

    buyGemNoFee@withrevert(e, usr, gemAmt);

    bool revert1 = e.msg.value > 0;
    bool revert2 = budSender != 1;
    bool revert3 = kusdInWad > max_uint256;
    bool revert4 = kusdAllowanceSenderPsm < kusdInWad;
    bool revert5 = kusdBalanceOfSender < kusdInWad;
    bool revert6 = gemAllowancePocketPsm < to_mathint(gemAmt);
    bool revert7 = gemBalanceOfPocket < to_mathint(gemAmt);
    bool revert8 = tout == max_uint256;

    assert lastReverted <=> revert1 || revert2 || revert3 ||
                            revert4 || revert5 || revert6 ||
                            revert7 || revert8, "Revert rules failed";
}

// Verify correct storage changes for non reverting fill
rule fill() {
    env e;

    bytes32 ilk = ilk();
    address pocket = pocket();
    mathint to18ConversionFactor = to18ConversionFactor();

    mathint vatDebtBefore = vat.debt();
    mathint vatLineBefore = vat.Line();
    mathint vatIlkArtBefore; mathint a; mathint b; mathint vatIlkLineBefore; mathint c;
    vatIlkArtBefore, a, b, vatIlkLineBefore, c = vat.ilks(ilk);
    mathint kusdBalanceOfPsmBefore = kusd.balanceOf(currentContract);
    mathint gemBalanceOfPocketBefore = gem.balanceOf(pocket);

    mathint calcWad = min(
                        min(
                            subCap(gemBalanceOfPocketBefore * to18ConversionFactor + buf(), vatIlkArtBefore),
                            subCap(vatIlkLineBefore / RAY(), vatIlkArtBefore)
                        ),
                        subCap(vatLineBefore, vatDebtBefore) / RAY()
                    );

    mathint wad = fill(e);

    mathint vatIlkArtAfter; mathint d;
    vatIlkArtAfter, a, b, c, d = vat.ilks(ilk);
    mathint kusdBalanceOfPsmAfter = kusd.balanceOf(currentContract);

    assert wad == calcWad, "fill did not return the expected wad";
    assert vatIlkArtAfter == vatIlkArtBefore + wad, "fill did not increase vat.ilks(ilk).Art by wad";
    assert kusdBalanceOfPsmAfter == kusdBalanceOfPsmBefore + wad, "fill did not increase kusd.balanceOf(psm) by wad";
}

// Verify revert rules on fill
rule fill_revert() {
    env e;

    bytes32 ilk = ilk();
    address pocket = pocket();
    mathint to18ConversionFactor = to18ConversionFactor();
    mathint buf = buf();

    mathint vatLive = vat.live();
    mathint vatDebt = vat.debt();
    mathint vatLine = vat.Line();
    mathint vatUrnInk; mathint vatUrnArt;
    vatUrnInk, vatUrnArt = vat.urns(ilk, currentContract);
    mathint vatIlkArt; mathint vatIlkRate; mathint vatIlkSpot; mathint vatIlkLine; mathint vatIlkDust;
    vatIlkArt, vatIlkRate, vatIlkSpot, vatIlkLine, vatIlkDust = vat.ilks(ilk);
    require vatUrnArt == vatIlkArt;
    require vatIlkDust == 0;
    mathint kusdJoinLive = kusdJoin.live();
    mathint vatKusdPsm = vat.kusd(currentContract);
    mathint vatKusdKusdJoin = vat.kusd(kusdJoin);
    mathint vatCanKusdJoinPsm = vat.can(currentContract, kusdJoin);
    mathint gemBalanceOfPocket = gem.balanceOf(pocket);
    require kusd.wards(kusdJoin) == 1;
    mathint kusdTotalSupply = kusd.totalSupply();
    require kusdTotalSupply >= to_mathint(kusd.balanceOf(currentContract));

    mathint wad = min(
                        min(
                            subCap(gemBalanceOfPocket * to18ConversionFactor + buf, vatIlkArt),
                            subCap(vatIlkLine / RAY(), vatIlkArt)
                        ),
                        subCap(vatLine, vatDebt) / RAY()
                    );

    fill@withrevert(e);

    bool revert1  = e.msg.value > 0;
    bool revert2  = vatIlkRate != RAY();
    bool revert3  = gemBalanceOfPocket * to18ConversionFactor + buf > max_uint256;
    bool revert4  = wad == 0;
    bool revert5  = vatLive != 1;
    bool revert6  = vatUrnArt + wad > max_uint256;
    bool revert7  = vatIlkArt + wad > max_uint256;
    bool revert8  = wad * RAY() > max_int256();
    bool revert9  = vatDebt + (wad * RAY()) > max_uint256;
    bool revert10 = vatUrnInk * vatIlkSpot > max_uint256;
    bool revert11 = (vatUrnArt + wad) * RAY() > vatUrnInk * vatIlkSpot;
    bool revert12 = vatKusdPsm + wad * RAY() > max_uint256;
    bool revert13 = kusdJoinLive != 1;
    bool revert14 = vatCanKusdJoinPsm != 1;
    bool revert15 = vatKusdKusdJoin + (wad * RAY()) > max_uint256;
    bool revert16 = kusdTotalSupply + wad > max_uint256;

    assert lastReverted <=> revert1  || revert2  || revert3  ||
                            revert4  || revert5  || revert6  ||
                            revert7  || revert8  || revert9  ||
                            revert10 || revert11 || revert12 ||
                            revert13 || revert14 || revert15 ||
                            revert16, "Revert rules failed";
}

// Verify correct storage changes for non reverting trim
rule trim() {
    env e;

    bytes32 ilk = ilk();
    address pocket = pocket();
    mathint to18ConversionFactor = to18ConversionFactor();

    mathint vatIlkArtBefore; mathint a; mathint b; mathint vatIlkLineBefore; mathint c;
    vatIlkArtBefore, a, b, vatIlkLineBefore, c = vat.ilks(ilk);
    mathint kusdBalanceOfPsmBefore = kusd.balanceOf(currentContract);
    mathint gemBalanceOfPocketBefore = gem.balanceOf(pocket);

    mathint calcWad = min(
                        max(
                            subCap(vatIlkArtBefore, gemBalanceOfPocketBefore * to18ConversionFactor + buf()),
                            subCap(vatIlkArtBefore, vatIlkLineBefore / RAY())
                        ),
                        kusdBalanceOfPsmBefore
                    );

    mathint wad = trim(e);

    mathint vatIlkArtAfter; mathint d;
    vatIlkArtAfter, a, b, c, d = vat.ilks(ilk);
    mathint kusdBalanceOfPsmAfter = kusd.balanceOf(currentContract);

    assert wad == calcWad, "trim did not return the expected wad";
    assert vatIlkArtAfter == vatIlkArtBefore - wad, "trim did not decrease vat.ilks(ilk).Art by wad";
    assert kusdBalanceOfPsmAfter == kusdBalanceOfPsmBefore - wad, "trim did not decrease kusd.balanceOf(psm) by wad";
}

// Verify revert rules on trim
rule trim_revert() {
    env e;

    bytes32 ilk = ilk();
    address pocket = pocket();
    mathint to18ConversionFactor = to18ConversionFactor();
    mathint buf = buf();

    mathint vatLive = vat.live();
    mathint vatDebt = vat.debt();
    mathint vatLine = vat.Line();
    mathint vatUrnInk; mathint vatUrnArt;
    vatUrnInk, vatUrnArt = vat.urns(ilk, currentContract);
    mathint vatIlkArt; mathint vatIlkRate; mathint vatIlkSpot; mathint vatIlkLine; mathint vatIlkDust;
    vatIlkArt, vatIlkRate, vatIlkSpot, vatIlkLine, vatIlkDust = vat.ilks(ilk);
    require vatIlkSpot == RAY(); // Fix 1:1 price to avoid timeout
    require vatUrnArt == vatIlkArt;
    require vatIlkDust == 0;
    require vatDebt >= vatIlkArt * RAY();
    mathint vatKusdPsm = vat.kusd(currentContract);
    mathint vatKusdKusdJoin = vat.kusd(kusdJoin);
    mathint gemBalanceOfPocket = gem.balanceOf(pocket);
    mathint kusdBalanceOfPsm = kusd.balanceOf(currentContract);
    mathint kusdAllowancePsmKusdJoin = kusd.allowance(currentContract, kusdJoin);
    require to_mathint(kusd.totalSupply()) >= kusdBalanceOfPsm;

    mathint wad = min(
                        max(
                            subCap(vatIlkArt, gemBalanceOfPocket * to18ConversionFactor + buf),
                            subCap(vatIlkArt, vatIlkLine / RAY())
                        ),
                        kusdBalanceOfPsm
                    );

    trim@withrevert(e);

    bool revert1  = e.msg.value > 0;
    bool revert2  = vatIlkRate != RAY();
    bool revert3  = gemBalanceOfPocket * to18ConversionFactor + buf > max_uint256;
    bool revert4  = wad == 0;
    bool revert5  = vatKusdKusdJoin < wad * RAY();
    bool revert6  = vatKusdPsm + wad * RAY() > max_uint256;
    bool revert7  = kusdBalanceOfPsm < wad;
    bool revert8  = kusdAllowancePsmKusdJoin < wad;
    bool revert9  = vatLive != 1;
    bool revert10 = wad * RAY() > max_int256();
    bool revert11 = vatUrnInk * vatIlkSpot > max_uint256;

    assert lastReverted <=> revert1  || revert2  || revert3  ||
                            revert4  || revert5  || revert6  ||
                            revert7  || revert8  || revert9  ||
                            revert10 || revert11, "Revert rules failed";
}

// Verify correct storage changes for non reverting chug
rule chug() {
    env e;

    bytes32 ilk = ilk();
    address pocket = pocket();
    mathint to18ConversionFactor = to18ConversionFactor();

    mathint a; mathint vatUrnPsmArt;
    a, vatUrnPsmArt = vat.urns(ilk, currentContract);
    mathint kusdBalanceOfPsmBefore = kusd.balanceOf(currentContract);
    mathint gemBalanceOfPocketBefore = gem.balanceOf(pocket);
    address vow = vow();
    mathint vatKusdVowBefore = vat.kusd(vow);

    mathint calcWad = min(
                        kusdBalanceOfPsmBefore,
                        kusdBalanceOfPsmBefore + gemBalanceOfPocketBefore * to18ConversionFactor - vatUrnPsmArt
                    );

    mathint wad = chug(e);

    mathint kusdBalanceOfPsmAfter = kusd.balanceOf(currentContract);
    mathint vatKusdVowAfter = vat.kusd(vow);

    assert wad == calcWad, "chug did not return the expected wad";
    assert kusdBalanceOfPsmAfter == kusdBalanceOfPsmBefore - wad, "chug did not decrease kusd.balanceOf(psm) by wad";
    assert vow != kusdJoin => vatKusdVowAfter == vatKusdVowBefore + wad * RAY(), "chug did not increase vat.kusd(vow) by wad * RAY";
}

// Verify revert rules on chug
rule chug_revert() {
    env e;

    bytes32 ilk = ilk();
    address pocket = pocket();
    mathint to18ConversionFactor = to18ConversionFactor();

    address vow = vow();

    mathint a; mathint vatUrnPsmArt;
    a, vatUrnPsmArt = vat.urns(ilk, currentContract);
    mathint kusdBalanceOfPsm = kusd.balanceOf(currentContract);
    mathint gemBalanceOfPocket = gem.balanceOf(pocket);
    mathint kusdAllowancePsmKusdJoin = kusd.allowance(currentContract, kusdJoin);
    mathint vatKusdKusdJoin = vat.kusd(kusdJoin);
    mathint vatKusdVow = vat.kusd(vow);
    require kusd.totalSupply() >= kusd.balanceOf(currentContract);

    mathint wad = min(
                        kusdBalanceOfPsm,
                        kusdBalanceOfPsm + gemBalanceOfPocket * to18ConversionFactor - vatUrnPsmArt
                    );

    chug@withrevert(e);

    bool revert1 = e.msg.value > 0;
    bool revert2 = vow == 0;
    bool revert3 = kusdBalanceOfPsm + gemBalanceOfPocket * to18ConversionFactor > max_uint256;
    bool revert4 = kusdBalanceOfPsm + gemBalanceOfPocket * to18ConversionFactor - vatUrnPsmArt < 0;
    bool revert5 = wad == 0;
    bool revert6 = kusdAllowancePsmKusdJoin < wad;
    bool revert7 = vatKusdKusdJoin < wad * RAY();
    bool revert8 = wad * RAY() > max_uint256;
    bool revert9 = vow != kusdJoin && vatKusdVow + wad * RAY() > max_uint256;

    assert lastReverted <=> revert1 || revert2 || revert3 ||
                            revert4 || revert5 || revert6 ||
                            revert7 || revert8 || revert9, "Revert rules failed";
}

// Verify correct return value comes from rush getter
rule rush() {
    bytes32 ilk = ilk();
    address pocket = pocket();
    mathint to18ConversionFactor = to18ConversionFactor();
    mathint buf = buf();

    mathint vatDebt = vat.debt();
    mathint vatLine = vat.Line();
    mathint vatIlkArt; mathint a; mathint b; mathint vatIlkLine; mathint c;
    vatIlkArt, a, b, vatIlkLine, c = vat.ilks(ilk);
    mathint gemBalanceOfPocket = gem.balanceOf(pocket);

    mathint calcWad = min(
                        min(
                            subCap(gemBalanceOfPocket * to18ConversionFactor + buf, vatIlkArt),
                            subCap(vatIlkLine / RAY(), vatIlkArt)
                        ),
                        subCap(vatLine, vatDebt) / RAY()
                    );

    mathint wad = rush();

    assert wad == calcWad, "rush did not return the expected wad";
}

// Verify revert rules on rush getter
rule rush_revert() {
    bytes32 ilk = ilk();
    address pocket = pocket();
    mathint to18ConversionFactor = to18ConversionFactor();
    mathint buf = buf();

    mathint a; mathint vatIlkRate; mathint b; mathint c; mathint d;
    a, vatIlkRate, b, c, d = vat.ilks(ilk);
    mathint gemBalanceOfPocket = gem.balanceOf(pocket);

    rush@withrevert();

    bool revert1 = vatIlkRate != RAY();
    bool revert2 = gemBalanceOfPocket * to18ConversionFactor + buf > max_uint256;

    assert lastReverted <=> revert1 || revert2, "Revert rules failed";
}

// Verify correct return value comes from gush getter
rule gush() {
    bytes32 ilk = ilk();
    address pocket = pocket();
    mathint to18ConversionFactor = to18ConversionFactor();
    mathint buf = buf();

    mathint vatIlkArt; mathint a; mathint b; mathint vatIlkLine; mathint c;
    vatIlkArt, a, b, vatIlkLine, c = vat.ilks(ilk);
    mathint gemBalanceOfPocket = gem.balanceOf(pocket);
    mathint kusdBalanceOfPsm = kusd.balanceOf(currentContract);

    mathint calcWad = min(
                        max(
                            subCap(vatIlkArt, gemBalanceOfPocket * to18ConversionFactor + buf),
                            subCap(vatIlkArt, vatIlkLine / RAY())
                        ),
                        kusdBalanceOfPsm
                    );

    mathint wad = gush();

    assert wad == calcWad, "gush did not return the expected wad";
}

// Verify revert rules on gush getter
rule gush_revert() {
    bytes32 ilk = ilk();
    address pocket = pocket();
    mathint to18ConversionFactor = to18ConversionFactor();
    mathint buf = buf();

    mathint a; mathint vatIlkRate; mathint b; mathint c; mathint d;
    a, vatIlkRate, b, c, d = vat.ilks(ilk);
    mathint gemBalanceOfPocket = gem.balanceOf(pocket);

    gush@withrevert();

    bool revert1 = vatIlkRate != RAY();
    bool revert2 = gemBalanceOfPocket * to18ConversionFactor + buf > max_uint256;

    assert lastReverted <=> revert1 || revert2, "Revert rules failed";
}

// Verify correct return value comes from cut getter
rule cut() {
    bytes32 ilk = ilk();
    address pocket = pocket();
    mathint to18ConversionFactor = to18ConversionFactor();

    mathint a; mathint vatUrnPsmArt;
    a, vatUrnPsmArt = vat.urns(ilk, currentContract);
    mathint kusdBalanceOfPsm = kusd.balanceOf(currentContract);
    mathint gemBalanceOfPocket = gem.balanceOf(pocket);

    mathint calcWad = min(
                        kusdBalanceOfPsm,
                        kusdBalanceOfPsm + gemBalanceOfPocket * to18ConversionFactor - vatUrnPsmArt
                    );

    mathint wad = cut();

    assert wad == calcWad, "cut did not return the expected wad";
}

// Verify revert rules on cut getter
rule cut_revert() {
    bytes32 ilk = ilk();
    address pocket = pocket();
    mathint to18ConversionFactor = to18ConversionFactor();

    mathint a; mathint vatUrnPsmArt;
    a, vatUrnPsmArt = vat.urns(ilk, currentContract);
    mathint kusdBalanceOfPsm = kusd.balanceOf(currentContract);
    mathint gemBalanceOfPocket = gem.balanceOf(pocket);

    cut@withrevert();

    bool revert1 = kusdBalanceOfPsm + gemBalanceOfPocket * to18ConversionFactor > max_uint256;
    bool revert2 = kusdBalanceOfPsm + gemBalanceOfPocket * to18ConversionFactor - vatUrnPsmArt < 0;

    assert lastReverted <=> revert1 || revert2, "Revert rules failed";
}

// Verify assets (kusd + gem) is always greater or equal to the Art
// This could be an invariant but is replaced with a rule for easier synthax
rule assetsGreaterOrEqualArt(method f) {
    env e;

    bytes32 ilk = ilk();
    address pocket = pocket();
    mathint to18ConversionFactor = to18ConversionFactor();

    mathint a; mathint vatUrnPsmArtBefore;
    a, vatUrnPsmArtBefore = vat.urns(ilk, currentContract);

    mathint kusdBalanceOfPsmBefore = kusd.balanceOf(currentContract);
    mathint kusdBalanceOfSenderBefore = kusd.balanceOf(e.msg.sender);

    mathint gemBalanceOfPocketBefore = gem.balanceOf(pocket);
    mathint gemBalanceOfSenderBefore = gem.balanceOf(e.msg.sender);

    mathint tinBefore = tin();
    mathint toutBefore = tout();

    require e.msg.sender != currentContract;
    require e.msg.sender != pocket;

    require kusdBalanceOfSenderBefore + kusdBalanceOfPsmBefore <= to_mathint(kusd.totalSupply());
    require gemBalanceOfSenderBefore + gemBalanceOfPocketBefore <= to_mathint(gem.totalSupply());

    require tinBefore <= WAD();
    require toutBefore <= WAD();

    // require invariant holds before
    require kusdBalanceOfPsmBefore + gemBalanceOfPocketBefore * to18ConversionFactor >= vatUrnPsmArtBefore;

    calldataarg arg;
    f(e, arg);

    mathint aAfter; mathint vatUrnPsmArtAfter;
    aAfter, vatUrnPsmArtAfter = vat.urns(ilk, currentContract);
    mathint kusdBalanceOfPsmAfter = kusd.balanceOf(currentContract);
    mathint gemBalanceOfPocketAfter = gem.balanceOf(pocket);

    // assert invariant holds after
    assert kusdBalanceOfPsmAfter + gemBalanceOfPocketAfter * to18ConversionFactor >= vatUrnPsmArtAfter;
}

// sellGem with tin as 0 has same effects as sellGemNoFee
rule sellGemEquivalence() {
    env e;

    address usr;
    uint256 gemAmt;

    mathint tin = tin();
    require tin == 0;

    storage initial = lastStorage;

    sellGem(e, usr, gemAmt);

    storage afterSell = lastStorage;

    sellGemNoFee(e, usr, gemAmt) at initial;

    storage afterSellNoFee = lastStorage;

    assert afterSell[currentContract] == afterSellNoFee[currentContract], "psm storage different";
    assert afterSell[gem] == afterSellNoFee[gem], "gem storage different";
    assert afterSell[kusd] == afterSellNoFee[kusd], "kusd storage different";
}

// buyGem with tout as 0 has same effects as buyGemNoFee
rule buyGemEquivalence() {
    env e;

    address usr;
    uint256 gemAmt;

    mathint tout = tout();
    require tout == 0;

    storage initial = lastStorage;

    buyGem(e, usr, gemAmt);

    storage afterBuy = lastStorage;

    buyGemNoFee(e, usr, gemAmt) at initial;

    storage afterBuyNoFee = lastStorage;

    assert afterBuy[currentContract] == afterBuyNoFee[currentContract], "psm storage different";
    assert afterBuy[gem] == afterBuyNoFee[gem], "gem storage different";
    assert afterBuy[kusd] == afterBuyNoFee[kusd], "kusd storage different";
}

// if fill is possible trim is not possible and vice-versa
rule fillOrTrim() {
    env e;

    storage initial = lastStorage;

    fill@withrevert(e);

    bool fillSucceed = !lastReverted;

    trim@withrevert(e) at initial;

    bool trimSucceed = !lastReverted;

    assert fillSucceed => !trimSucceed;
    assert trimSucceed => !fillSucceed;
}

// fill() injects rush()
rule fillsRush() {
    env e;

    mathint rushed = rush();
    mathint filled = fill(e);

    assert rushed > 0 && rushed == filled;
}

// trim removes gush()
rule trimsGush() {
    env e;

    mathint gushed = gush();
    mathint trimmed = trim(e);

    assert gushed > 0 && gushed == trimmed;
}
