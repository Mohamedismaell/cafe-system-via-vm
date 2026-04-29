import tkinter as tk
from tkinter import messagebox, ttk
import csv, os, sys, subprocess

# ── Theme ────────────────────────────────────────────────────────
CREAM="#F3E9DC"; CARAMEL="#C08552"; BROWNIE="#5E3023"
COFFEE="#895737"; WHITE="#FFFFFF"; LIGHT_BR="#D4A96A"; DANGER="#C0392B"

FT=("Georgia",13,"bold"); FB=("Georgia",10,"bold")
FS=("Georgia",9);         FP=("Georgia",12,"bold"); FC=("Georgia",11)

BASE=os.path.dirname(os.path.abspath(__file__))
MENU=os.path.join(BASE,"data","menu.csv")
CART=os.path.join(BASE,"data","cart.csv")

# ── Data ─────────────────────────────────────────────────────────
def load_menu():
    if not os.path.exists(MENU):
        messagebox.showerror("Error",f"menu.csv not found!\n{MENU}"); return []
    try:
        with open(MENU,newline="",encoding="utf-8") as f:
            rows=list(csv.DictReader(f))
        return [{"name":r["item_name"].strip(),"price":float(r.get("price",0)),
                 "quantity":int(r.get("quantity",0)),"category":r.get("category","General").strip()}
                for r in rows if r.get("item_name","").strip()]
    except Exception as e:
        messagebox.showerror("Error",str(e)); return []

def write_cart(cart):
    os.makedirs(os.path.dirname(CART),exist_ok=True)
    with open(CART,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["item_name","quantity","price"])
        [w.writerow([n,d["qty"],d["price"]]) for n,d in cart.items()]

# ── App ──────────────────────────────────────────────────────────
class OrderApp:
    def __init__(self,root,dashboard_window=None):
        self.root=root; self.dash=dashboard_window
        self.root.title("☕ Corner Café — Order")
        self.root.state("zoomed"); self.root.configure(bg=CREAM)
        self.items=load_menu(); self.cart={}
        self.sv=tk.StringVar(); self.sv.trace("w",lambda *_:self.render())
        self.cv=tk.StringVar(value="All")
        self._ui(); self.render()

    def _btn(self,parent,text,bg,cmd,hover=None,**kw):
        hbg=hover or LIGHT_BR
        b=tk.Button(parent,text=text,bg=bg,fg=WHITE,font=FB,relief="flat",
                    bd=0,cursor="hand2",command=cmd,
                    activebackground=hbg,activeforeground=BROWNIE,**kw)
        b.bind("<Enter>",lambda e,b=b,c=hbg:b.config(bg=c))
        b.bind("<Leave>",lambda e,b=b,c=bg:b.config(bg=c))
        return b

    def _ui(self):
        # Header
        tk.Frame(self.root,bg=BROWNIE,height=6).pack(fill="x")
        h=tk.Frame(self.root,bg=BROWNIE,pady=12); h.pack(fill="x")
        tk.Label(h,text="☕  CORNER CAFÉ — New Order",font=("Georgia",17,"bold"),
                 bg=BROWNIE,fg=CREAM).pack(side="left",padx=20)
        tk.Frame(self.root,bg=CARAMEL,height=3).pack(fill="x")

        # Toolbar
        tb=tk.Frame(self.root,bg=COFFEE,pady=8); tb.pack(fill="x")
        self._btn(tb,"⬅  Dashboard",BROWNIE,self._back,padx=14,pady=6).pack(side="left",padx=12)
        sf=tk.Frame(tb,bg=WHITE,highlightthickness=1,highlightbackground=CARAMEL)
        sf.pack(side="left",padx=16,ipadx=4,ipady=2)
        tk.Label(sf,text="🔍",bg=WHITE,fg=COFFEE,font=FC).pack(side="left",padx=4)
        tk.Entry(sf,textvariable=self.sv,bg=WHITE,fg=BROWNIE,relief="flat",
                 font=FC,width=26,insertbackground=BROWNIE).pack(side="left",ipady=4,padx=(0,6))
        cats=["All"]+sorted({i["category"] for i in self.items})
        cb=ttk.Combobox(tb,textvariable=self.cv,values=cats,state="readonly",font=FS,width=14)
        cb.pack(side="left",padx=4,ipady=3)
        self.cv.trace("w",lambda *_:self.render())
        self.badge=tk.Label(tb,text="",font=FS,bg=COFFEE,fg=CREAM)
        self.badge.pack(side="right",padx=16)

        # Body
        body=tk.Frame(self.root,bg=CREAM); body.pack(fill="both",expand=True)

        # LEFT – menu
        left=tk.Frame(body,bg=CREAM); left.pack(side="left",fill="both",expand=True,padx=(12,4),pady=10)
        tk.Label(left,text="Menu",font=("Georgia",16,"bold"),bg=CREAM,fg=BROWNIE).pack(anchor="w",pady=(0,6))
        wrap=tk.Frame(left,bg=CREAM); wrap.pack(fill="both",expand=True)
        self.canvas=tk.Canvas(wrap,bg=CREAM,highlightthickness=0)
        vsb=tk.Scrollbar(wrap,orient="vertical",command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right",fill="y"); self.canvas.pack(side="left",fill="both",expand=True)
        self.sf=tk.Frame(self.canvas,bg=CREAM)
        self.cw=self.canvas.create_window((0,0),window=self.sf,anchor="nw")
        self.sf.bind("<Configure>",lambda e:self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",lambda e:self.canvas.itemconfig(self.cw,width=e.width))
        self.canvas.bind_all("<MouseWheel>",lambda e:self.canvas.yview_scroll(int(-e.delta/120),"units"))
        self.canvas.bind_all("<Button-4>",lambda e:self.canvas.yview_scroll(-1,"units"))
        self.canvas.bind_all("<Button-5>",lambda e:self.canvas.yview_scroll(1,"units"))

        # RIGHT – cart
        right=tk.Frame(body,bg=WHITE,highlightthickness=2,highlightbackground=CARAMEL)
        right.pack(side="right",fill="y",padx=(4,12),pady=10,ipadx=4)
        ch=tk.Frame(right,bg=BROWNIE,pady=10); ch.pack(fill="x")
        tk.Label(ch,text="🛒  Your Cart",font=("Georgia",13,"bold"),bg=BROWNIE,fg=CREAM).pack()
        lw=tk.Frame(right,bg=WHITE); lw.pack(fill="both",expand=True,padx=8,pady=8)
        csb=tk.Scrollbar(lw,orient="vertical")
        self.cl=tk.Listbox(lw,font=FC,bg=CREAM,fg=BROWNIE,selectbackground=CARAMEL,
                           selectforeground=WHITE,relief="flat",bd=0,width=32,
                           activestyle="none",yscrollcommand=csb.set)
        csb.config(command=self.cl.yview); csb.pack(side="right",fill="y"); self.cl.pack(fill="both",expand=True)
        tk.Frame(right,bg=CARAMEL,height=2).pack(fill="x",padx=8)
        self.tot=tk.Label(right,text="Total:  0.00 EGP",font=("Georgia",13,"bold"),
                          bg=WHITE,fg=BROWNIE,pady=8); self.tot.pack()
        bf=tk.Frame(right,bg=WHITE); bf.pack(fill="x",padx=10,pady=(0,10))
        self._btn(bf,"💾  Save & Send to Checkout",CARAMEL,self._save,pady=9).pack(fill="x",pady=(0,6))
        self._btn(bf,"🗑  Clear Cart",BROWNIE,self._clear,hover=DANGER,pady=9).pack(fill="x")

        # Footer
        ft=tk.Frame(self.root,bg=BROWNIE,pady=6); ft.pack(fill="x",side="bottom")
        tk.Label(ft,text="© 2025 Corner Café System  |  All rights reserved",
                 font=FS,bg=BROWNIE,fg=CARAMEL).pack()

    def render(self):
        for w in self.sf.winfo_children(): w.destroy()
        q=self.sv.get().lower(); cat=self.cv.get()
        data=[i for i in self.items if q in i["name"].lower() and (cat=="All" or i["category"]==cat)]
        self.badge.config(text=f"  {len(data)} item(s)  ")
        if not data:
            tk.Label(self.sf,text="No items found.",font=FC,bg=CREAM,fg=COFFEE,pady=30).pack(); return
        for item in data:
            ok=item["quantity"]>0
            card=tk.Frame(self.sf,bg=WHITE,highlightthickness=1,highlightbackground=CARAMEL,padx=18,pady=14)
            card.pack(fill="x",padx=12,pady=6)
            tr=tk.Frame(card,bg=WHITE); tr.pack(fill="x")
            tk.Label(tr,text=item["name"],font=FT,bg=WHITE,fg=BROWNIE).pack(side="left")
            tk.Label(tr,text=f"  {item['category']}  ",font=FS,bg=CARAMEL,fg=WHITE,padx=4,pady=2).pack(side="right")
            ir=tk.Frame(card,bg=WHITE); ir.pack(fill="x",pady=(4,8))
            tk.Label(ir,text=f"{item['price']:.2f} EGP",font=FP,bg=WHITE,fg=COFFEE).pack(side="left")
            sc="#4CAF50" if item["quantity"]>10 else (DANGER if item["quantity"]==0 else "#E8A020")
            tk.Label(ir,text=f"  Stock: {item['quantity']}",font=FS,bg=WHITE,fg=sc).pack(side="left",padx=10)
            br=tk.Frame(card,bg=WHITE); br.pack(anchor="w")
            self._btn(br,"➕  Add",CARAMEL if ok else "#CCC",lambda i=item:self._add(i),
                      padx=18,pady=6,state="normal" if ok else "disabled").pack(side="left",padx=(0,8))
            self._btn(br,"➖  Remove",BROWNIE,lambda i=item:self._rem(i),
                      hover=DANGER,padx=18,pady=6).pack(side="left")
        self.canvas.yview_moveto(0)

    def _add(self,item):
        n=item["name"]
        self.cart[n]=self.cart.get(n,{"qty":0,"price":item["price"]})
        self.cart[n]["qty"]+=1; self._refresh_cart()

    def _rem(self,item):
        n=item["name"]
        if n in self.cart:
            self.cart[n]["qty"]-=1
            if self.cart[n]["qty"]<=0: del self.cart[n]
        self._refresh_cart()

    def _refresh_cart(self):
        self.cl.delete(0,tk.END); total=0
        for n,d in self.cart.items():
            lt=d["qty"]*d["price"]; total+=lt
            self.cl.insert(tk.END,f"  {n}  ×{d['qty']}  =  {lt:.2f} EGP")
        self.tot.config(text=f"Total:  {total:.2f} EGP")

    def _clear(self):
        if self.cart and messagebox.askyesno("Clear","Remove all items?"):
            self.cart.clear(); self._refresh_cart()

    def _save(self):
        if not self.cart:
            messagebox.showwarning("Empty","Add at least one item first."); return
        write_cart(self.cart)
        messagebox.showinfo("Saved ✓","Cart saved! Open Checkout to process payment.")

    def _back(self):
        self.root.destroy()
        if self.dash:
            try: self.dash.deiconify(); self.dash.state("zoomed"); return
            except: pass
        dash=os.path.join(BASE,"dashboard.py")
        if os.path.exists(dash): subprocess.Popen([sys.executable,dash])

if __name__=="__main__":
    root=tk.Tk(); OrderApp(root); root.mainloop()