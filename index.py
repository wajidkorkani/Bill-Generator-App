import customtkinter as ctk
from fpdf import FPDF
from datetime import datetime
import os

ctk.set_appearance_mode("dark") 

# Global storage for history
data = {}
order_counter = 1

class BillApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bill Generator (Per-Item Discount)")
        self.geometry("850x600")

        self.items = []  # Stores (name, price, discount_pct, final_price)
        self.total_bill = 0.0
        self.total_discount = 0.0

        # --- UI LAYOUT ---
        self.grid_columnconfigure(1, weight=1)
        
        # Left Panel
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.item_name = ctk.CTkEntry(self.input_frame, placeholder_text="Item Name")
        self.item_name.pack(pady=10, padx=20)

        self.item_price = ctk.CTkEntry(self.input_frame, placeholder_text="Price (PKR)")
        self.item_price.pack(pady=10, padx=20)
        
        
        self.discount_entry = ctk.CTkEntry(self.input_frame)
        self.discount_entry.pack(pady=5, padx=20)
        self.discount_entry.insert(0, "0")

        self.add_button = ctk.CTkButton(
            self.input_frame, text="Add Item", command=self.add_item
        )
        self.add_button.pack(pady=20)

        self.print_button = ctk.CTkButton(
            self.input_frame, text="Print to PDF",
            fg_color="#2ecc71", hover_color="#27ae60", command=self.print_bill
        )
        self.print_button.pack(pady=10)

        self.history_button = ctk.CTkButton(
            self.input_frame, text="Print History Report",
            fg_color="#3498db", hover_color="#2980b9", command=self.print_history
        )
        self.history_button.pack(pady=10)

        self.clear_button = ctk.CTkButton(
            self.input_frame, text="Clear All",
            fg_color="#e74c3c", command=self.clear_bill
        )
        self.clear_button.pack(pady=10)

        # Right Panel
        self.display_frame = ctk.CTkTextbox(self, width=500, font=("Courier New", 13))
        self.display_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.update_display()

    def add_item(self):
        try:
            name = self.item_name.get()
            price = float(self.item_price.get())
            disc_pct = float(self.discount_entry.get())
            
            if name:
                # Calculate discount for this specific item
                item_disc_amount = price * (disc_pct / 100)
                final_price = price - item_disc_amount
                
                self.items.append((name, price, disc_pct, final_price))
                self.total_bill += final_price
                self.total_discount += item_disc_amount
                
                self.update_display()

                # Reset inputs for next item
                self.item_name.delete(0, 'end')
                self.item_price.delete(0, 'end')
                self.discount_entry.delete(0, 'end')
                self.discount_entry.insert(0, "0")
        except ValueError:
            pass

    def update_display(self):
        self.display_frame.delete("0.0", "end")
        header = f"{'ITEM':<15} {'PRICE':>10} {'DISC%':>8} {'TOTAL':>10}\n"
        self.display_frame.insert("0.0", header)
        self.display_frame.insert("end", "-" * 48 + "\n")

        for name, price, disc, final in self.items:
            row = f"{name[:14]:<15} {price:>10.2f} {disc:>7.0f}% {final:>10.2f}\n"
            self.display_frame.insert("end", row)

        self.display_frame.insert("end", "\n" + "-" * 48 + "\n")
        self.display_frame.insert("end", f"{'TOTAL SAVINGS':<33} PKR {self.total_discount:>10.2f}\n")
        self.display_frame.insert("end", f"{'GRAND TOTAL':<33} PKR {self.total_bill:>10.2f}")

    def clear_bill(self):
        self.items = []
        self.total_bill = 0.0
        self.total_discount = 0.0
        self.update_display()

    def print_bill(self):
        global order_counter
        if not self.items:
            return

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save current state to history
        data[order_counter] = {
            "date": date_str,
            "items": list(self.items),
            "total_discount": self.total_discount,
            "total_final": self.total_bill
        }

        # Generate Receipt PDF
        filename = f"receipt_{order_counter}.pdf"
        pdf = FPDF(unit='mm', format=(80, 150))
        pdf.add_page()
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, "Wajid's Shop", ln=True, align='C')
        
        pdf.set_font("Arial", size=8)
        pdf.cell(0, 5, f"Date: {date_str}", ln=True, align='C')
        pdf.ln(5)

        pdf.set_font("Courier", size=8)
        pdf.cell(0, 5, f"{'Item':<15} {'Disc':>5} {'Price':>10}", ln=True)
        pdf.cell(0, 2, "-"*35, ln=True)

        for name, price, disc, final in self.items:
            pdf.cell(0, 5, f"{name[:14]:<15} {disc:>4.0f}% {final:>10.2f}", ln=True)

        pdf.ln(5)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 6, f"Total Savings: PKR {self.total_discount:.2f}", ln=True)
        pdf.cell(0, 7, f"GRAND TOTAL: PKR {self.total_bill:.2f}", ln=True)

        pdf.output(filename)
        
        print(f"Bill #{order_counter} printed.")
        order_counter += 1
        self.clear_bill()

    def print_history(self):
        if not data:
            print("No history to print!")
            return

        filename = "sales_history.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Sales History Report", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 10)
        pdf.cell(15, 10, "ID", 1)
        pdf.cell(50, 10, "Date", 1)
        pdf.cell(40, 10, "Saved", 1)
        pdf.cell(40, 10, "Final Total", 1, ln=True)

        pdf.set_font("Arial", size=10)
        total_revenue = 0

        for order_id, info in data.items():
            pdf.cell(15, 10, str(order_id), 1)
            pdf.cell(50, 10, info['date'], 1)
            pdf.cell(40, 10, f"{info['total_discount']:.2f}", 1)
            pdf.cell(40, 10, f"{info['total_final']:.2f}", 1, ln=True)
            total_revenue += info['total_final']

        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"Total Cumulative Revenue: PKR {total_revenue:.2f}", ln=True, align='R')

        pdf.output(filename)
        print(f"History report generated: {filename}")

if __name__ == "__main__":
    app = BillApp()
    app.mainloop()