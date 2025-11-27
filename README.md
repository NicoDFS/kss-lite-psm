# `kss-lite-psm`

Lightweight Peg Stability Module (LitePSM) implementation.

## Table of Contents

<!-- vim-markdown-toc GFM -->

- [Deployments](#deployments)
- [Overview](#overview)
- [Architecture](#architecture)
  - [Design and Constraints](#design-and-constraints)
  - [Known Limitations](#known-limitations)
    - [1. Potential Front-Running](#1-potential-front-running)
    - [2. No Slippage Protection](#2-no-slippage-protection)
    - [3. No Support for Upgradeable Gems](#3-no-support-for-upgradeable-gems)
    - [4. Emergency Shutdown](#4-emergency-shutdown)
- [Contributing](#contributing)

<!-- vim-markdown-toc -->

## Deployments

| Network          | Chain ID | Description  | Address                                                                                                               |
| :------          | -------: | :----------  | :------                                                                                                               |
| Ethereum Mainnet | 1        | Gem (USDC)   | [`0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48`][usdc] |
|                  |          | Lite PSM     | [`0xf6e72Db5454dd049d0788e411b06CfAF16853042`][lite-psm]                                                              |
|                  |          | Pocket       | [`0x37305B1cD40574E4C5Ce33f8e8306Be057fD7341`][pocket]                                                                |
|                  |          | Lite PSM Mom | [`0x467b32b0407Ad764f56304420Cddaa563bDab425`][lite-psm-mom]                                                          |

  [usdc]: https://etherscan.io/address/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
  [lite-psm]: https://etherscan.io/address/0xf6e72Db5454dd049d0788e411b06CfAF16853042
  [pocket]: https://etherscan.io/address/0x37305B1cD40574E4C5Ce33f8e8306Be057fD7341
  [lite-psm-mom]: https://etherscan.io/address/0x467b32b0407Ad764f56304420Cddaa563bDab425

## Overview

A Peg Stability Module (PSM) is a facility through which users can freely swap Kusd for stablecoins with no slippage.
KalyDAO Governance can enable swap fees, though, which are computed as revenue for the protocol.

This module is heavily inspired by MakerDAO's PSM implementations and other PSM prototypes within KalyDAO repositories.

The issue with those implementations is that swapping through them can be quite gas intensive, because they manipulate
the `Vat` (KalyDAO's main accounting module) directly on every swap.

To help alleviate this problem, `KssLitePsm` aims to be more gas efficient. The strategy is to allow users to swap in a
**pool** of pre-minted Kusd and stablecoins, reducing the swap to 2 ERC-20 token transfers with little overhead.

The required bookkeeping is done _off-band_ (not to be confused with _off-chain_), through a set of permissionless
functions that aim to keep the pool operating under the predefined constraints, and incorporate the accumulated swap
fees into the protocol's surplus buffer.

Furthermore, there is a new requirement &ndash; related to KalyDAO Endgame &ndash; to allow authorized parties to swap
through the PSM without paying any fees, even if they have been activated by Governance. Apart from the existing
permissionless `buyGem` / `sellGem` functions, this iteration introduces `buyGemNoFee` / `sellGemNoFee` permissioned
counterparties.

Last, but not least, in this version `gem` balance **can** be held in a different address to allow the protocol to
receive yield from stablecoins that require the custody of the assets to be segregated. This address can be either an
orphaned EOA or a bespoke smart contract. The only constraint is that `KssLitePsm` **should** be able to freely move any
amount of `gem` on behalf of such address.

## Architecture

A simplified diagram of the `KssLitePsm` architecture:

```
                                                buyGemNoFee /
                                           ╭────────────────────────  🤴
 ╭─────────╮                               │    sellGemNoFee      Whitelisted
 │         │       transferFrom            │                         User
 │   Gem   ◄────────────────────────────╮  │
 │         │                            │  │
 ╰────▲────╯                            │  │
      │                                 │  │
      │                                 │  │
      │ approve ·····╮                  │  │
      │              ╎                  │  │
╭─────┴────╮         ╎          ╭───────┴──▼───╮
│          │         ╎          │              │     buyGem /
│  Pocket  │         ╰·········>│  KssLitePsm  ◄────────────────────  🧑
│          │                    │              │     sellGem         User
╰──────────╯                    ╰─┬──┬──┬──▲─▲─╯
                                  │  │  │  │ │
                                  │  │  │  │ │
                 frob             │  │  │  │ │
     ╭────────────────────────────╯  │  │  │ │
     │                               │  │  │ │
     │                               │  │  │ │
     │                               │  │  │ │ fill / trim / chug
     │                   join / exit │  │  │ ╰──────────────────────  👷
     │                               │  │  │                        Keeper
     │                               │  │  │
╭────▼────╮          ╭───────────╮   │  │  │           ╭─────────────────╮   
│         │   move   │           │   │  │  │   file    │                 │   
│   Vat   ◄──────────┤  KusdJoin  ◄───╯  │  ╰───────────│  KssLitePsmMom  │   
│         │          │           │      │              │                 │   
╰─────────╯          ╰─────┬─────╯      │              ╰─────────────────╯   
                           │            │
                           │            │
               mint / burn │            │
                           │            │ transfer / transferFrom
                           │            │
                      ╭────▼────╮       │
                      │         │       │
                      │   Kusd   ◄───────╯
                      │         │
                      ╰─────────╯
```

### Design and Constraints

These are the main constraints that guided the design of this module:

1. Gas efficiency: make swaps as cheap in terms of gas as possible, without sacrificing security and readability.
1. Backwards compatibility: the new implementation should not break integrations with the current one.
1. Permissioned no-fee swaps: specific actors are allowed to use the PSM for swaps without paying any swap fees.

Part of the Kusd liquidity available in `KssLitePsm` is technically unbacked Kusd. This not a problem because the Kusd is
locked into `KssLitePsm` until users deposit USDC, backing the amount that is going to be released.

### Known Limitations

#### 1. Potential Front-Running

`KssLitePsm` relies on pre-minted Kusd. It is designed to keep a fixed-sized amount (`buf`) of it available most of the
time.  However, when users call `buyGem`, the amount of Kusd available will be temporarily larger than `buf`.

**Scenario A:** a user might observe the outstanding amount of Kusd and wish to call `sellGem` to receive the total of
Kusd in return. In that scenario, there is a possibility of a transaction calling any of the permissionless bookkeeping
functions to front-run them, causing the swap to fail, as the Kusd liquidity would be lower than the required amount.

The scenario A above is not possible with the current PSM implementation because each swap is "self-balancing", so no
off-band bookkeeping is required.

**Scenario B:** a large swap might front-run another one, even if unintentionally. Imagine there is `10M` Kusd
outstanding in `KssLitePsm`. If Alice &ndash; who wants to swap `8M` &ndash; and Bob &ndash; who wants to swap `3M`
&ndash; submit their transactions at the same time, only the first one will be executed.

The scenario B above is not possible with the current PSM implementation because `sellGem` is able to mint Kusd
on-the-fly to fulfill the swap, given that there is enough room in the debt ceiling.

Notice how the same issue happens in `buyGem`, however the amount of `gem` deposited into `KssLitePsm` is only bounded
by the debt ceiling, while the amount of `Kusd` will tend to gravitate towards `buf`.

The consequence is that anyone willing to call `sellGem` with a value larger than `buf` should take care of potential
front-running transactions by bundling it with an optional liquidity increase (`fill`).

#### 2. No Slippage Protection

Swaps in `KssLitePsm` are generally not subject to slippage. The only exception is when there is a KalyDAO Governance
proposal to increase the swapping fees `tin` and/or `tout`. That is done through an Executive Spell, which is an
on-chain smart contract that can be permissionlessly _cast_ (executed) after following the Governance process.

If Alice sends a swap transaction and a spell increasing the fees is cast before her transaction, she will either pay
more Kusd when buying gems or receive less Kusd when selling gems than the originally expected.

This is a highly unlikely scenario, but users or aggregators are able to handle this issue through a wrapper contract.

#### 3. No Support for Upgradeable Gems

We no longer have a dedicated `GemJoin` contract to normalize different token implementations. For instance, we lost the
capacity to identify upgrades in upgradeable tokens when compared to previous PSM iterations.

On the other hand, non-upgradeable gems that do not return `true` on `transfer`/`transferFrom` were not
previously supported, but we removed such restriction in this iteration.

#### 4. Emergency Shutdown

`KssLitePsm` assumes the ESM threshold is set large enough prior to its deployment, so Emergency Shutdown can never be
called.

## Contributing

To be able to run the integration tests, you need to set the `ETH_RPC_URL` env var to a valid Mainnet node:

```bash
ETH_RPC_URL='...' forge test -vvv
```

You can also use a `.env` file for that (see `.env.example`):

```bash
# .env
ETH_RPC_URL='...'
```

Then simply run:
```bash
forge test -vvv
```

---

## Testnet Deployment (KalyChain)

### Prerequisites

1. **Foundry installed**
   ```bash
   curl -L https://foundry.paradigm.xyz | bash
   foundryup
   ```

2. **Testnet KLC for gas** - Get from KalyChain testnet faucet

3. **Environment configured**
   ```bash
   cp .env.example .env
   nano .env  # Add your private key and configure addresses
   ```

### Testnet Configuration

KalyChain Testnet addresses:
- RPC: `https://testnetrpc.kalychain.io/rpc`
- Chain ID: `3889`
- Explorer: `https://testnet.kalyscan.io`

**Core Contracts:**
- Vat: `0x30e50aD44cd1890A6bf9F09Bf6b8AfE62a6a390D`
- KusdJoin: `0xB4d2fB8F90C018762CD403B690061CE04189e381`
- Vow: `0x12af8412fB89929E2C56b4b9ded7eaC06705d2DC`
- Kusd: `0xd15F19c457AaaCB7A389B305Dac8611Cd2294c36`

**Mock Collateral Tokens:**
- MockUSDC: `0x148d19609F3Ad595F8455225510f89cF0F121013`
- MockUSDT: `0xeE9940240B94821937812c43a6264e5aA417f161`
- MockWBTC: `0x92631B8Be684d41d0dF9eb473D9E3995CDb2a797`
- MockWETH: `0x68E7492e64FF0592a6D82E5C0323b8a8DDBfB884`
- MockDAI: `0x7BE7a4338143C417D2D71C96eA8560767c6E4477`

**Deployed PSMs:**
- USDC-A PSM: `0xF61448725934d38b7fF94f9162AEed729486de35`

### Deployment Steps

#### 1. Deploy and Configure

Run the deployment helper script. This script will:
1. Clean up previous deployment artifacts (prevents nonce errors)
2. Deploy the PSM contract
3. Authorize the PSM on the Vat (`rely`)
4. Set the debt ceiling (`line`)
5. Add collateral (`slip`) and convert to ink (`grab`)
6. Set the spot price (`spot`)
7. Configure the Vow address and buffer size
8. Approve the PSM to spend gems from the pocket

```bash
# Run deployment (handles cleanup and configuration automatically)
./deploy.sh
```

The script will output transaction hashes and the deployed PSM address.

**Alternative (manual command):**
If you prefer to run the forge script directly:

```bash
# Clean cache to prevent nonce errors
rm -rf broadcast/ cache/

# Run deployment script
yes | forge script script/KssLitePsmDeploy.s.sol \
  --rpc-url $RPC_URL \
  --private-key $PRIVATE_KEY \
  --broadcast \
  --legacy \
  --gas-limit 10000000 \
  --gas-price 30000000000 \
  --no-cache \
  -vvv
```



#### 2. Test PSM

```bash
# Set PSM address from deployment output
export PSM_ADDRESS=0xF61448725934d38b7fF94f9162AEed729486de35

# Fill PSM with KUSD
cast send $PSM_ADDRESS "fill()" \
  --rpc-url $RPC_URL \
  --private-key $PRIVATE_KEY \
  --gas-limit 500000 \
  --gas-price 21000000000 \
  --legacy

# Mint test USDC to your address
cast send 0x148d19609F3Ad595F8455225510f89cF0F121013 \
  "mint(address,uint256)" \
  $FOUNDRY_OWNER \
  1000000000000 \
  --rpc-url $RPC_URL \
  --private-key $PRIVATE_KEY \
  --gas-limit 500000 \
  --gas-price 21000000000 \
  --legacy

# Approve PSM to spend your USDC
cast send 0x148d19609F3Ad595F8455225510f89cF0F121013 \
  "approve(address,uint256)" \
  $PSM_ADDRESS \
  1000000000000 \
  --rpc-url $RPC_URL \
  --private-key $PRIVATE_KEY \
  --gas-limit 500000 \
  --gas-price 21000000000 \
  --legacy

# Test swap (1 USDC → 1 KUSD)
cast send $PSM_ADDRESS \
  "sellGem(address,uint256)" \
  $FOUNDRY_OWNER \
  1000000 \
  --rpc-url $RPC_URL \
  --private-key $PRIVATE_KEY \
  --gas-limit 500000 \
  --gas-price 21000000000 \
  --legacy

# Check your KUSD balance
cast call 0xd15F19c457AaaCB7A389B305Dac8611Cd2294c36 \
  "balanceOf(address)(uint256)" \
  $FOUNDRY_OWNER \
  --rpc-url $RPC_URL
```

---
