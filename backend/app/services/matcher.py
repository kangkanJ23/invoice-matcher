from datetime import datetime

class MatcherService:
    """
    Compares a PO and an Invoice.
    Detects mismatches, fraud flags, and computes a confidence score.
    """

    # ---------------------------------------------------------
    # Main matching function
    # ---------------------------------------------------------
    def match_po_and_invoice(self, po: dict, inv: dict) -> dict:
        mismatches = []
        fraud_flags = []
        score = 100.0

        # -----------------------------------------------------
        # 1. Total amount mismatch
        # -----------------------------------------------------
        po_total = po.get("grand_total")
        inv_total = inv.get("grand_total")

        if po_total and inv_total:
            try:
                diff_pct = abs(inv_total - po_total) / (po_total if po_total != 0 else 1)

                if diff_pct > 0.02:  # >2% mismatch
                    mismatches.append({
                        "type": "total_mismatch",
                        "po_total": po_total,
                        "invoice_total": inv_total,
                        "difference_percentage": diff_pct
                    })
                    score -= min(50, diff_pct * 100)
            except Exception:
                pass

        # -----------------------------------------------------
        # 2. Item-level matching (simple name check)
        # -----------------------------------------------------
        po_items = { (item.get("description") or "").lower(): item for item in (po.get("items") or []) }
        inv_items = { (item.get("description") or "").lower(): item for item in (inv.get("items") or []) }

        for name, p_item in po_items.items():
            if name not in inv_items:
                # fuzzy fallback: substring match
                matched = False
                for inv_name in inv_items.keys():
                    if name in inv_name or inv_name in name:
                        matched = True
                        break

                if not matched:
                    mismatches.append({
                        "type": "missing_item_in_invoice",
                        "item": name
                    })
                    score -= 10

        # -----------------------------------------------------
        # 3. Fraud flag: invoice date earlier than PO date
        # -----------------------------------------------------
        try:
            po_date = po.get("date")
            inv_date = inv.get("date")

            if po_date and inv_date:
                po_dt = datetime.fromisoformat(po_date)
                inv_dt = datetime.fromisoformat(inv_date)

                if inv_dt < po_dt:
                    fraud_flags.append("invoice_date_before_po")
                    score -= 15
        except Exception:
            pass

        # -----------------------------------------------------
        # 4. Vendor mismatch
        # -----------------------------------------------------
        po_vendor = (po.get("vendor_name") or "").lower()
        inv_vendor = (inv.get("vendor_name") or "").lower()

        if po_vendor and inv_vendor and po_vendor != inv_vendor:
            mismatches.append({
                "type": "vendor_mismatch",
                "po_vendor": po_vendor,
                "invoice_vendor": inv_vendor
            })
            score -= 8

        # -----------------------------------------------------
        # Final score formatting
        # -----------------------------------------------------
        score = max(0, round(score, 2))

        return {
            "mismatches": mismatches,
            "fraud_flags": fraud_flags,
            "score": score
        }
