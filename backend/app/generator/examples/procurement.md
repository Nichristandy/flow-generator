Start
User: Material Request
KTU: Approve MR
IF Approved
Procurement: Create PR
ELSE
GOTO Material Request
ENDIF
Procurement: RFQ
Vendor: Vendor Quotation
Procurement: Purchase Comparison
Procurement: Winner Selection
Procurement: Purchase Order
Stores: Goods Receipt
Vendor: Vendor Bill
Finance: Payment
End
