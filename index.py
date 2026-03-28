import customtkinter as ctk
from fpdf import FPDF
from datetime import datetime

ctk.set_appearance_mode("dark") 

class BillApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Modern Bill Generator with Discount")
        self.geometry("800x550")

        self.items = [] 
        self.subtotal = 0.0

        # --- UI LAYOUT ---
        self.grid_columnconfigure(1, weight=1)
        
        # Left Panel
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.item_name = ctk.CTkEntry(self.input_frame, placeholder_text="Item Name")
        self.item_name.pack(pady=10, padx=20)

        self.item_price = ctk.CTkEntry(self.input_frame, placeholder_text="Price ($)")
        self.item_price.pack(pady=10, padx=20)

        self.add_button = ctk.CTkButton(self.input_frame, text="Add Item", command=self.add_item)
        self.add_button.pack(pady=10)

        # Discount Input
        self.discount_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Discount % (e.g. 10)")
        self.discount_entry.pack(pady=10, padx=20)
        self.discount_entry.insert(0, "0") # Default to 0

        self.print_button = ctk.CTkButton(self.input_frame, text="Print to PDF", 
                                          fg_color="#2ecc71", hover_color="#27ae60",
                                          command=self.save_pdf)
        self.print_button.pack(pady=10)

        self.clear_button = ctk.CTkButton(self.input_frame, text="Clear All", fg_color="#e74c3c", 
                                          command=self.clear_bill)
        self.clear_button.pack(pady=10)

        # Right Panel (Receipt View)
        self.display_frame = ctk.CTkTextbox(self, width=450, font=("Courier New", 14))
        self.display_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.update_display()

    def add_item(self):
        try:
            name = self.item_name.get()
            price = float(self.item_price.get())
            if name:
                self.items.append((name, price))
                self.subtotal += price
                self.update_display()
                self.item_name.delete(0, 'end')
                self.item_price.delete(0, 'end')
        except ValueError:
            pass

    def get_discount(self):
        try:
            return float(self.discount_entry.get())
        except ValueError:
            return 0.0

    def update_display(self):
        disc_percent = self.get_discount()
        disc_amount = self.subtotal * (disc_percent / 100)
        grand_total = self.subtotal - disc_amount

        self.display_frame.delete("0.0", "end")
        self.display_frame.insert("0.0", f"{'ITEM':<25} {'PRICE':>10}\n")
        self.display_frame.insert("end", "-"*38 + "\n")
        for item, price in self.items:
            self.display_frame.insert("end", f"{item:<25} ${price:>9.2f}\n")
        
        self.display_frame.insert("end", "\n" + "-"*38 + "\n")
        self.display_frame.insert("end", f"{'SUBTOTAL':<25} ${self.subtotal:>9.2f}\n")
        self.display_frame.insert("end", f"{f'DISCOUNT ({disc_percent}%)':<25} -${disc_amount:>8.2f}\n")
        self.display_frame.insert("end", f"{'GRAND TOTAL':<25} ${grand_total:>9.2f}")

    def save_pdf(self):
        disc_percent = self.get_discount()
        disc_amount = self.subtotal * (disc_percent / 100)
        grand_total = self.subtotal - disc_amount

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, txt="OFFICIAL INVOICE", ln=True, align='C')
        pdf.ln(10)

        # Items Table
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(130, 10, "Item Description", border=1)
        pdf.cell(60, 10, "Price", border=1, ln=True)

        pdf.set_font("Arial", size=12)
        for item, price in self.items:
            pdf.cell(130, 10, item, border=1)
            pdf.cell(60, 10, f"${price:.2f}", border=1, ln=True)

        # Totals Section
        pdf.ln(5)
        pdf.cell(130, 10, "Subtotal:", align='R')
        pdf.cell(60, 10, f"${self.subtotal:.2f}", ln=True, align='R')
        
        pdf.cell(130, 10, f"Discount ({disc_percent}%):", align='R')
        pdf.cell(60, 10, f"-${disc_amount:.2f}", ln=True, align='R')
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(130, 15, "GRAND TOTAL:", align='R')
        pdf.cell(60, 15, f"${grand_total:.2f}", ln=True, align='R')

        filename = f"bill_{datetime.now().strftime('%H%M%S')}.pdf"
        pdf.output(filename)
        print(f"Generated: {filename}")

    def clear_bill(self):
        self.items = []
        self.subtotal = 0.0
        self.update_display()

if __name__ == "__main__":
    app = BillApp()
    # Refresh display when discount changes (optional: could add a trace)
    app.mainloop()