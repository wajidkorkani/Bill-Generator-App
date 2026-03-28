import customtkinter as ctk
from fpdf import FPDF
from datetime import datetime

ctk.set_appearance_mode("dark") 

class BillApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Modern Bill Generator")
        self.geometry("700x500")

        self.items = [] # Store items for the PDF
        self.total = 0.0

        # --- UI LAYOUT ---
        self.grid_columnconfigure(1, weight=1)
        
        # Left Panel
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.item_name = ctk.CTkEntry(self.input_frame, placeholder_text="Item Name")
        self.item_name.pack(pady=10, padx=20)

        self.item_price = ctk.CTkEntry(self.input_frame, placeholder_text="Price (PKR)")
        self.item_price.pack(pady=10, padx=20)

        self.add_button = ctk.CTkButton(self.input_frame, text="Add Item", command=self.add_item)
        self.add_button.pack(pady=10)

        self.print_button = ctk.CTkButton(self.input_frame, text="Print to PDF", 
                                          fg_color="green", hover_color="darkgreen",
                                          command=self.save_pdf)
        self.print_button.pack(pady=10)

        # Right Panel (Receipt View)
        self.display_frame = ctk.CTkTextbox(self, width=400)
        self.display_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.update_display()

    def add_item(self):
        try:
            name = self.item_name.get()
            price = float(self.item_price.get())
            if name:
                self.items.append((name, price))
                self.total += price
                self.update_display()
                self.item_name.delete(0, 'end')
                self.item_price.delete(0, 'end')
        except ValueError:
            pass

    def update_display(self):
        self.display_frame.delete("0.0", "end")
        self.display_frame.insert("0.0", f"{'ITEM':<20} {'PRICE':>10}\n")
        self.display_frame.insert("end", "-"*35 + "\n")
        for item, price in self.items:
            self.display_frame.insert("end", f"{item:<20} PKR{price:>9.2f}\n")
        self.display_frame.insert("end", "\n" + "-"*35 + "\n")
        self.display_frame.insert("end", f"{'TOTAL':<20} PKR{self.total:>9.2f}")

    def save_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="INVOICE", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
        pdf.ln(10)

        # Table Header
        pdf.cell(90, 10, "Item", border=1)
        pdf.cell(40, 10, "Price", border=1, ln=True)

        # Items
        for item, price in self.items:
            pdf.cell(90, 10, item, border=1)
            pdf.cell(40, 10, f"PKR{price:.2f}", border=1, ln=True)

        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(90, 10, "GRAND TOTAL")
        pdf.cell(40, 10, f"PKR{self.total:.2f}", ln=True)

        filename = f"bill_{datetime.now().strftime('%H%M%S')}.pdf"
        pdf.output(filename)
        print(f"Saved as {filename}")

if __name__ == "__main__":
    app = BillApp()
    app.mainloop()