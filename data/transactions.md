# Raw Transaction Logs (DIRTY_DUMP_V3_ISO20022)

## BATCH_001: High-Value Corporate Transfers
- 2026-Jan-02: User 'acc_8812' (alias: tech-hk-logistics) initiated a bulk transfer of $12,500.20 to AlphaHoldings (ACC-9901). Note: marked as 'repayment'.
- 03/01/26: ACC-9901 (Alpha) dispersed funds: $1.2k to acc-4421, $1.1k to acc-4422, $1.25k to acc-4423, $1.3k to acc-4424... (total 10 small txs). Looks like structuring.
- 2026.01.04: ACC-4421 -> ACC-000X ($1,150); ACC-4422 -> ACC-000X ($1,090); ACC-4423 -> ACC-000X ($1,210). All destination 'CaymanGlobal_Offshore'.

## BATCH_002: ISO 20022 Raw Message Fragments (Simulated)
```xml
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
  <CstmrCdtTrfInitn>
    <PmtId><EndToEndId>TXN-9988221</EndToEndId></PmtId>
    <Amt><InstdAmt Ccy="USD">500000.00</InstdAmt></Amt>
    <Dbtr><Nm>TechCorp HK</Nm><CtctDtls><PhneNb>+852-2345-XXXX</PhneNb></CtctDtls></Dbtr>
    <UltmtDbtr><Nm>BVI-Investments-99</Nm></UltmtDbtr>
    <Cdtr><Nm>Consultant_X</Nm></Cdtr>
    <UltmtCdtr><Nm>John Smith</Nm></UltmtCdtr>
    <SplmtryData>Ref: Project Alpha-Omega. TYPO: Shpping Fees.</SplmtryData>
  </CstmrCdtTrfInitn>
</Document>
```
- RAW_HEX: 49534f32303032325f54584e5f414c455254 (Flagged for 'Unusual Ultimate Debtor' hierarchy).

## BATCH_003: The 'Tsuen Wan' Smurfing Ring (Mule-Cluster-Alpha)
- 2026-01-05: 45 individual payments received by ACC-7721. Each payment is exactly $9,995.00 (just under the $10k trigger).
- Senders: ACC-101 through ACC-145. All accounts share registration IP: 192.168.1.102.
- 2026-01-05 14:22: ACC-101 (Tsuen Wan resident) -> $9,995 -> ACC-7721
- 2026-01-05 14:23: ACC-102 (Tsuen Wan resident) -> $9,995 -> ACC-7721
- 2026-01-05 14:25: ACC-103 (Tsuen Wan resident) -> $9,995 -> ACC-7721
- ...[LOG_TRUNCATED]... 42 more identical transactions.
- ANALYSIS: Funds were aggregated at ACC-7721 and then moved to 'Vanguard-Wealth-Mgmt' (linked to John Smith).

## BATCH_004: Circular jurisdictional Loop
- T_01_06: 'CaymanGlobal_Offshore' (ACC-000X) -> $100,000 -> 'Transit-Acc-99'.
- T_01_07: 'Transit-Acc-99' -> $95,000 -> 'Panama-Cloud-Holdings'.
- T_01_08: 'Panama-Cloud-Holdings' -> $90,000 -> 'Shell-Parent BVI'.
- RESULT: Funds returned to original beneficiary hierarchy via circular layering.

## BATCH_005: Sanctions & Blacklist Hits
- 2026-01-10: Payment of $2,500,000.00 from 'NorthStar Trading' (Blacklisted/Sanctioned) to 'Oceanic-Freight-Services'. 
- oceanic-Freight-Services is a 100% subsidiary of 'TechCorp HK'.
- 2026-01-11: Oceanic-Freight-Services dispersed $500,000 into 500 individual 'Gift Card' accounts ($1,000 each) to anonymize the cashout.
- 12/Jan/2026: Zhang_W (Director) -> ACC-1122 ($5,000). Status: Pending. Note: 'Consultancy for Sanctioned-Entity-Z'.

## BATCH_006: ISO 20022 Cross-Border (pain.001)
```xml
<PmtId><InstrId>REF-6677</InstrId></PmtId>
<Amt><InstdAmt Ccy="HKD">1000000.00</InstdAmt></Amt>
<Dbtr><Nm>Seychelles-Secret-Trust</Nm></Dbtr>
<Cdtr><Nm>Mystery-Buyer-Z</Nm></Cdtr>
<RltdRmtInf><Ustrd>Purchase of Equity Interest in Panama-Cloud-Holdings</Ustrd></RltdRmtInf>
```
- ALERT: This transaction confirms the 'Mystery-Buyer-Z' conflict mentioned in the Entities record.
