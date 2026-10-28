import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from deadlock import bankers_safety, request_resources, detect_deadlock, need_matrix

BG="#101827"; PANEL="#172235"; ALT="#22314A"; TEXT="#EAF0FA"; MUTED="#A8B5C9"
BLUE="#70A5FF"; GREEN="#36C995"; RED="#FF6B7A"; YELLOW="#F4C66A"

class App:
    def __init__(self, root):
        self.root=root; root.title("DeadlockGuard | OS Resource Manager")
        root.geometry("1180x830"); root.minsize(920,680); root.configure(bg=BG)
        self.n=tk.StringVar(value="5"); self.m=tk.StringVar(value="3")
        self.alloc=[]; self.maximum=[]; self.req=[]; self.avail=[]
        self.last_result=None; self.last_kind=""
        self.build()
        self.load_sample()

    def label(self,p,t,size=10,color=TEXT,bold=False):
        return tk.Label(p,text=t,bg=p.cget("bg"),fg=color,font=("Segoe UI",size,"bold" if bold else "normal"))
    def entry(self,p,v,w=5):
        return tk.Entry(p,textvariable=v,width=w,bg=ALT,fg=TEXT,insertbackground=TEXT,relief="flat",justify="center")
    def button(self,p,t,cmd,primary=False):
        return tk.Button(p,text=t,command=cmd,bg=BLUE if primary else ALT,
          fg="#0B1424" if primary else TEXT,activebackground="#8AB6FF",relief="flat",bd=0,
          padx=10,pady=7,font=("Segoe UI",9,"bold"),cursor="hand2")
    def build(self):
        h=tk.Frame(self.root,bg=BG); h.pack(fill="x",padx=18,pady=12)
        tk.Label(h,text="DeadlockGuard",bg=BG,fg=BLUE,font=("Segoe UI",23,"bold")).pack(side="left")
        self.label(h,"OPERATING SYSTEMS PROJECT",9,MUTED,True).pack(side="right",pady=10)
        bar=tk.Frame(self.root,bg=PANEL,padx=10,pady=9); bar.pack(fill="x",padx=18,pady=(0,8))
        self.label(bar,"Processes",9,MUTED).pack(side="left")
        self.entry(bar,self.n,4).pack(side="left",padx=5)
        self.label(bar,"Resource types",9,MUTED).pack(side="left",padx=(10,0))
        self.entry(bar,self.m,4).pack(side="left",padx=5)
        self.button(bar,"Apply Size",self.apply_size).pack(side="left",padx=7)
        self.button(bar,"Load Sample",self.load_sample).pack(side="left",padx=4)
        self.button(bar,"Export CSV",self.export).pack(side="right")
        self.matrix_frame=tk.Frame(self.root,bg=BG); self.matrix_frame.pack(fill="both",expand=True,padx=18,pady=4)
        out=tk.Frame(self.root,bg=PANEL,padx=12,pady=10); out.pack(fill="both",expand=True,padx=18,pady=8)
        self.label(out,"ANALYSIS RESULTS",10,BLUE,True).pack(anchor="w")
        self.status=tk.Label(out,text="Ready.",bg=PANEL,fg=MUTED,anchor="w",font=("Segoe UI",10))
        self.status.pack(fill="x",pady=6)
        self.output=tk.Text(out,height=8,bg=BG,fg=TEXT,insertbackground=TEXT,relief="flat",wrap="word",
                            font=("Consolas",10),padx=10,pady=8)
        self.output.pack(fill="both",expand=True)
        actions=tk.Frame(self.root,bg=BG); actions.pack(fill="x",padx=18,pady=(0,12))
        self.button(actions,"Check Safe State (Banker's)",self.run_bankers,True).pack(side="left",padx=(0,5))
        self.button(actions,"Test Resource Request",self.ask_request).pack(side="left",padx=5)
        self.button(actions,"Detect Deadlock",self.run_detection).pack(side="left",padx=5)
        self.button(actions,"Show Resource Graph",self.graph).pack(side="left",padx=5)

    def old(self,data,i,j,default="0"):
        try: return str(data[i][j])
        except (IndexError,TypeError): return default
    def build_matrices(self,old_a=None,old_max=None,old_req=None,old_av=None):
        for w in self.matrix_frame.winfo_children(): w.destroy()
        n,m=self.n_count,self.m_count
        old_a=old_a or []; old_max=old_max or []; old_req=old_req or []; old_av=old_av or []
        self.alloc=[]; self.maximum=[]; self.req=[]; self.avail=[]
        panels=[]
        for title in ("ALLOCATION","MAXIMUM CLAIM","CURRENT REQUEST + AVAILABLE"):
            p=tk.Frame(self.matrix_frame,bg=PANEL,padx=7,pady=8)
            p.pack(side="left",fill="both",expand=True,padx=4)
            self.label(p,title,9,BLUE,True).grid(row=0,column=0,columnspan=m+1,sticky="w",pady=(0,6))
            self.label(p,"Process",8,MUTED).grid(row=1,column=0,padx=2)
            for j in range(m): self.label(p,f"R{j}",8,MUTED).grid(row=1,column=j+1,padx=2)
            panels.append(p)
        for i in range(n):
            rows=[]
            for k,p in enumerate(panels):
                self.label(p,f"P{i}",8).grid(row=i+2,column=0,padx=2,pady=2)
                vs=[]
                source=[old_a,old_max,old_req][k]
                for j in range(m):
                    v=tk.StringVar(value=self.old(source,i,j))
                    self.entry(p,v,4).grid(row=i+2,column=j+1,padx=2,pady=2)
                    vs.append(v)
                rows.append(vs)
            self.alloc.append(rows[0]); self.maximum.append(rows[1]); self.req.append(rows[2])
        for k,p in enumerate(panels):
            caption=("Allocated resources","Maximum claim","Outstanding requests")
            self.label(p,caption[k],8,MUTED).grid(row=n+2,column=0,columnspan=m+1,sticky="w",pady=(6,0))
        p=panels[2]
        self.label(p,"Available",8,GREEN).grid(row=n+3,column=0,pady=(10,2))
        for j in range(m):
            v=tk.StringVar(value=self.old([old_av],0,j))
            self.entry(p,v,4).grid(row=n+3,column=j+1,padx=2,pady=(10,2)); self.avail.append(v)

    def readmat(self,mat):
        try: return [[int(v.get()) for v in row] for row in mat]
        except ValueError: raise ValueError("All matrix cells must contain whole numbers.")
    def state(self):
        try:
            return self.readmat(self.alloc),self.readmat(self.maximum),[int(v.get()) for v in self.avail],self.readmat(self.req)
        except ValueError: raise ValueError("All cells must contain whole numbers.")

    def apply_size(self):
        try: n,m=int(self.n.get()),int(self.m.get())
        except ValueError: messagebox.showerror("Invalid size","Enter integer sizes."); return
        if not 1<=n<=12 or not 1<=m<=8:
            messagebox.showerror("Invalid size","Choose 1–12 processes and 1–8 resource types."); return
        try: a,ma,av,r=self.state()
        except ValueError: a=ma=r=[]; av=[]
        self.n_count,self.m_count=n,m
        self.build_matrices(a,ma,r,av)
        self.status.configure(text=f"Model resized to {n} processes and {m} resource types.",fg=MUTED)

    def load_sample(self):
        self.n.set("5"); self.m.set("3"); self.n_count=5; self.m_count=3
        a=[[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]]
        ma=[[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]]
        r=[[0,0,0] for _ in range(5)]; av=[3,3,2]
        self.build_matrices(a,ma,r,av)
        self.status.configure(text="Classic Banker's example loaded. Click Check Safe State.",fg=MUTED)
        self.show("Sample loaded. Select an analysis action below.")

    def show(self,text):
        self.output.delete("1.0","end"); self.output.insert("1.0",text)

    def run_bankers(self):
        try: a,ma,av,_=self.state(); res=bankers_safety(a,ma,av)
        except ValueError as e: messagebox.showerror("Input error",str(e)); return
        self.last_result=res; self.last_kind="Banker's safety"
        lines=["BANKER'S SAFETY ANALYSIS","="*32,"Need = Maximum - Allocation"]
        lines += [f"P{i}: {row}" for i,row in enumerate(res["need"])]
        lines.append("")
        if res["safe"]:
            lines += ["RESULT: SAFE STATE","Safe sequence: "+" -> ".join(f"P{i}" for i in res["sequence"]),
                      "All processes can finish in this order."]
            self.status.configure(text="Safe state detected.",fg=GREEN)
        else:
            lines += ["RESULT: UNSAFE STATE","No complete safe sequence exists for the current state.",
                      "Unfinished processes: "+", ".join(f"P{i}" for i in res["unfinished"])]
            self.status.configure(text="Unsafe state detected.",fg=RED)
        lines.append(f"Final Work vector: {res['final_work']}")
        self.show("\\n".join(lines))

    def ask_request(self):
        try: a,ma,av,_=self.state()
        except ValueError as e: messagebox.showerror("Input error",str(e)); return
        win=tk.Toplevel(self.root); win.title("Test Resource Request"); win.configure(bg=PANEL)
        win.resizable(False,False); frame=tk.Frame(win,bg=PANEL,padx=16,pady=16); frame.pack()
        self.label(frame,"Simulate a resource request",12,TEXT,True).grid(row=0,column=0,columnspan=2,sticky="w",pady=(0,10))
        pv=tk.StringVar(value="P0")
        self.label(frame,"Process",9,MUTED).grid(row=1,column=0,sticky="w")
        ttk.Combobox(frame,textvariable=pv,values=[f"P{i}" for i in range(self.n_count)],state="readonly",width=8).grid(row=1,column=1,pady=4)
        vars=[]
        for j in range(self.m_count):
            self.label(frame,f"Request for R{j}",9,MUTED).grid(row=2+j,column=0,sticky="w",pady=3)
            v=tk.StringVar(value="0"); self.entry(frame,v,8).grid(row=2+j,column=1,pady=3); vars.append(v)
        def submit():
            try: req=[int(v.get()) for v in vars]; p=int(pv.get()[1:])
            except ValueError: messagebox.showerror("Invalid request","Request values must be integers.",parent=win); return
            try: result=request_resources(a,ma,av,p,req)
            except ValueError as e: messagebox.showerror("Invalid request",str(e),parent=win); return
            self.last_result=result; self.last_kind="Resource request"
            lines=["RESOURCE REQUEST ANALYSIS","="*32,f"Process: P{p}",f"Request: {req}",
                   "DECISION: "+("GRANTED" if result["granted"] else "NOT GRANTED"),result["reason"]]
            if result.get("safety"):
                sr=result["safety"]
                lines.append("Safe sequence: "+(" -> ".join(f"P{i}" for i in sr["sequence"]) if sr["safe"] else "none"))
            if result["granted"]:
                for i in range(self.n_count):
                    for j in range(self.m_count): self.alloc[i][j].set(str(result["allocation"][i][j]))
                for j in range(self.m_count): self.avail[j].set(str(result["available"][j]))
                self.status.configure(text="Request granted; allocation and available values updated.",fg=GREEN)
            else: self.status.configure(text="Request was not granted.",fg=YELLOW)
            self.show("\\n".join(lines)); win.destroy()
        self.button(frame,"Check Request",submit,True).grid(row=2+self.m_count,column=0,columnspan=2,sticky="ew",pady=(10,0))

    def run_detection(self):
        try: a,_,av,r=self.state(); res=detect_deadlock(a,r,av)
        except ValueError as e: messagebox.showerror("Input error",str(e)); return
        self.last_result=res; self.last_kind="Deadlock detection"
        lines=["DEADLOCK DETECTION","="*32,f"Available / Work: {av}",""]
        if res["deadlock"]:
            lines += ["RESULT: DEADLOCK / BLOCKED PROCESSES FOUND",
                      "Unfinished processes: "+", ".join(f"P{i}" for i in res["deadlocked_processes"]),
                      "Review their outstanding requests and allocated resources."]
            self.status.configure(text="Unfinished processes detected by the algorithm.",fg=RED)
        else:
            lines += ["RESULT: NO DEADLOCK DETECTED","All processes can finish under the current request matrix."]
            self.status.configure(text="No deadlock detected.",fg=GREEN)
        lines.append(f"Final Work vector: {res['final_work']}")
        self.show("\\n".join(lines))

    def graph(self):
        try: a,_,_,r=self.state()
        except ValueError as e: messagebox.showerror("Input error",str(e)); return
        win=tk.Toplevel(self.root); win.title("Resource Allocation Graph"); win.geometry("820x520"); win.configure(bg=BG)
        self.label(win,"Resource Allocation Graph",14,TEXT,True).pack(anchor="w",padx=14,pady=(12,2))
        self.label(win,"Blue arrow: allocation (R → P) | Yellow dashed arrow: request (P → R)",9,MUTED).pack(anchor="w",padx=14)
        c=tk.Canvas(win,bg=PANEL,highlightthickness=0); c.pack(fill="both",expand=True,padx=14,pady=12)
        win.update_idletasks(); w=max(c.winfo_width(),780); h=max(c.winfo_height(),430)
        pc={}; rc={}
        for i in range(self.n_count):
            x=90; y=45+i*(h-90)/max(1,self.n_count-1); pc[i]=(x,y)
            c.create_oval(x-25,y-18,x+25,y+18,fill="#254C7D",outline=BLUE,width=2)
            c.create_text(x,y,text=f"P{i}",fill="white",font=("Segoe UI",10,"bold"))
        for j in range(self.m_count):
            x=w-90; y=45+j*(h-90)/max(1,self.m_count-1); rc[j]=(x,y)
            c.create_rectangle(x-28,y-21,x+28,y+21,fill="#24584E",outline=GREEN,width=2)
            c.create_text(x,y,text=f"R{j}",fill="white",font=("Segoe UI",10,"bold"))
        for i in range(self.n_count):
            for j in range(self.m_count):
                if a[i][j]:
                    x1,y1=rc[j]; x2,y2=pc[i]
                    c.create_line(x1-28,y1,x2+25,y2,fill=BLUE,width=2,arrow="last")
                    c.create_text((x1+x2)/2,(y1+y2)/2+9,text=f"{a[i][j]} allocated",fill=TEXT,font=("Segoe UI",8))
                if r[i][j]:
                    x1,y1=pc[i]; x2,y2=rc[j]
                    c.create_line(x1+25,y1,x2-28,y2,fill=YELLOW,width=2,dash=(5,3),arrow="last")
                    c.create_text((x1+x2)/2,(y1+y2)/2-9,text=f"{r[i][j]} requested",fill=TEXT,font=("Segoe UI",8))

    def export(self):
        if not self.last_result: messagebox.showinfo("No results","Run an analysis first."); return
        path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV files","*.csv")],initialfile="deadlockguard_report.csv")
        if not path: return
        try:
            with open(path,"w",newline="",encoding="utf-8") as f:
                wr=csv.writer(f); wr.writerow(["DeadlockGuard - Operating Systems Project"])
                wr.writerow(["Analysis type",self.last_kind]); wr.writerow(["Result"])
                for key,value in self.last_result.items(): wr.writerow([key,repr(value)])
            messagebox.showinfo("Export complete",f"Saved report to:\\n{path}")
        except OSError as e: messagebox.showerror("Export failed",str(e))

def main():
    root=tk.Tk(); App(root); root.mainloop()
if __name__=="__main__": main()
