"""Presentación por vistas; no contiene lógica de resolución."""
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from sudoku.execution import score
from sudoku.generator import DIFFICULTIES

BG = '#f6f5f1'
WHITE = '#ffffff'
INK = '#283e40'
MUTED = '#748581'
TEAL = '#287b69'
SOFT = '#e5f1eb'


class Button(tk.Canvas):
    """Botón redondeado, con foco de teclado y estados explícitos."""
    def __init__(self, parent, text, command, *, primary=False, height=48, **kwargs):
        super().__init__(parent, height=height, width=160, bg=parent.cget('bg'),
                         highlightthickness=0, takefocus=1, **kwargs)
        self.text, self.command, self.primary = text, command, primary
        self.state = 'normal'
        self.selected = self.hover = False
        self.bind('<Configure>', self.paint)
        self.bind('<Enter>', lambda e: self._hover(True))
        self.bind('<Leave>', lambda e: self._hover(False))
        self.bind('<Button-1>', lambda e: self.invoke())
        self.bind('<Return>', lambda e: self.invoke())
        self.bind('<space>', lambda e: self.invoke())
        self.bind('<FocusIn>', self.paint)
        self.bind('<FocusOut>', self.paint)

    def _hover(self, value):
        self.hover = value
        self.paint()

    def config(self, **kwargs):
        for key in ('text', 'state', 'selected'):
            if key in kwargs:
                setattr(self, key, kwargs.pop(key))
        if kwargs:
            super().config(**kwargs)
        self.paint()

    def invoke(self):
        if self.state != 'disabled':
            self.focus_set()
            self.command()

    def paint(self, event=None):
        self.delete('all')
        w, h = self.winfo_width(), self.winfo_height()
        disabled = self.state == 'disabled'
        fill = '#e9eae5' if disabled else (TEAL if self.primary else (SOFT if self.selected or self.hover else WHITE))
        color = '#a1aaa5' if disabled else (WHITE if self.primary else INK)
        radius = 16
        points = [radius,2,w-radius,2,w-2,2,w-2,radius,w-2,h-radius,w-2,h-2,
                  w-radius,h-2,radius,h-2,2,h-2,2,h-radius,2,radius,2,2]
        self.create_polygon(points,smooth=True,fill=fill,
                            outline=TEAL if self.selected or self.focus_get()==self else fill,width=2)
        self.create_text(w/2,h/2,text=self.text,fill=color,font=('Segoe UI',11,'bold'))
        self.configure(cursor='arrow' if disabled else 'hand2')


class Views:
    def label(self, parent, text='', *, size=11, bold=False, color=INK, **kwargs):
        kwargs.setdefault('wraplength',350)
        return tk.Label(parent,text=text,bg=parent.cget('bg'),fg=color,
                        font=('Segoe UI',size,'bold' if bold else 'normal'),**kwargs)

    def button(self, parent, text, command, **kwargs):
        button = Button(parent,text,command,**kwargs)
        button.pack(fill='x',pady=4)
        return button

    def _build(self):
        self.view = 'home'
        self.difficulty = tk.StringVar(value='Fácil')
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TCombobox',font=('Segoe UI',11),padding=9,
                        fieldbackground=WHITE,background=WHITE,foreground=INK,arrowsize=16)
        style.map('TCombobox',fieldbackground=[('readonly',WHITE)],selectbackground=[('readonly',WHITE)],selectforeground=[('readonly',INK)])
        self.root.configure(bg=BG)
        self.viewport = tk.Canvas(self.root,bg=BG,highlightthickness=0)
        self.viewport.pack(fill='both',expand=True)
        self.content = tk.Frame(self.viewport,bg=BG)
        self.window = self.viewport.create_window(0,0,anchor='n',window=self.content)
        self.viewport.bind('<Configure>',self._layout)
        self.content.bind('<Configure>',lambda e:self._scroll_region())
        self.root.bind('<MouseWheel>',self._wheel)
        self.root.bind('<Next>',lambda e:self.viewport.yview_scroll(1,'pages'))
        self.root.bind('<Prior>',lambda e:self.viewport.yview_scroll(-1,'pages'))
        self.root.bind('<FocusIn>',self._reveal_focus,add='+')
        self.screens = {name:tk.Frame(self.content,bg=BG,padx=22,pady=20) for name in ('home','difficulty','game','summary','benchmark')}
        self._home()
        self._difficulty()
        self._game()
        self._summary()
        self._benchmark()
        self.show('home')

    def _layout(self, event):
        width = min(520,event.width)
        self.viewport.coords(self.window,event.width/2,0)
        self.viewport.itemconfigure(self.window,width=width)
        self._scroll_region()

    def _scroll_region(self):
        # Include the full viewport width: using only the centered content's
        # bounding box lets Tk shift the horizontal origin during initial layout.
        self.viewport.configure(scrollregion=(0,0,self.viewport.winfo_width(),
            max(self.content.winfo_height(),self.viewport.winfo_height())))
        self.viewport.xview_moveto(0)

    def _wheel(self, event):
        if event.widget.winfo_toplevel() == self.root:
            self.viewport.yview_scroll(int(-event.delta/120),'units')

    def _reveal_focus(self, event):
        widget = event.widget
        if widget.winfo_toplevel() != self.root or widget == self.root:
            return
        y = widget.winfo_rooty()-self.content.winfo_rooty()
        height = max(1,self.content.winfo_height())
        visible_top = self.viewport.canvasy(0)
        visible_bottom = visible_top+self.viewport.winfo_height()
        if y < visible_top or y+widget.winfo_height()>visible_bottom:
            self.viewport.yview_moveto(max(0,y-20)/height)

    def show(self, name):
        if name in ('home','benchmark'):
            self.refresh_benchmark_tables()
        for frame in self.screens.values():
            frame.pack_forget()
        self.view = name
        self.screens[name].pack(fill='x')
        self.root.update_idletasks()
        self._scroll_region()
        self.viewport.yview_moveto(0)
        self.draw()

    def _home(self):
        p = self.screens['home']
        self.label(p,'S U D O K U   S T U D I O',size=10,color=TEAL,bold=True).pack(pady=(22,18))
        art = tk.Canvas(p,width=82,height=82,bg=BG,highlightthickness=0)
        art.pack()
        for r in range(3):
            for c in range(3):
                x,y = c*27,r*27
                art.create_oval(x+2,y+2,x+25,y+25,fill=TEAL if (r,c)==(1,1) else '#dce8df',outline='')
        self.label(p,'Crea el mejor algoritmo',size=24,bold=True,justify='center').pack(pady=(18,26))
        self.menu_generate = self.button(p,'Generar sudoku',lambda:self.show('difficulty'),primary=True)
        self.scan_button = self.button(p,'Escanear sudoku',lambda:None)
        self.scan_button.config(state='disabled')
        self.button(p,'Historial',self.comparison)
        self.button(p,'Benchmark',lambda:self.show('benchmark'))
        self.button(p,'Salir',self.close)
        self.label(p,'Clasificación benchmark',bold=True).pack(pady=(24,10))
        table = tk.Frame(p,bg=WHITE)
        table.pack(fill='x')
        widths = (2,1,1,1,1,1)
        for col,weight in enumerate(widths):
            table.columnconfigure(col,weight=weight)
        for col,title in enumerate(('Algoritmo','Fácil','Inter.','Difícil','Extremo','Media')):
            tk.Label(table,text=title,bg=SOFT,fg=INK,font=('Segoe UI',8,'bold'),padx=2,pady=8).grid(row=0,column=col,sticky='nsew')
        self.benchmark_summary = table
        self.benchmark_summary_rows = []

    def refresh_benchmark_tables(self):
        results = self.history.benchmark_results()
        for widgets in self.benchmark_summary_rows:
            for widget in widgets:
                widget.destroy()
        self.benchmark_summary_rows = []
        shown = results[:5]
        if not shown:
            label = tk.Label(self.benchmark_summary,text='Ejecuta el primer benchmark',bg=WHITE,
                             fg=MUTED,font=('Segoe UI',10),pady=12)
            label.grid(row=1,column=0,columnspan=6,sticky='nsew')
            self.benchmark_summary_rows.append([label])
        for row,result in enumerate(shown,1):
            values = (result['algorithm'],f"{result['Fácil']:.0f}%",f"{result['Intermedio']:.0f}%",
                      f"{result['Difícil']:.0f}%",f"{result['Extremo']:.0f}%",f"{result['overall']:.1f}%")
            widgets = []
            for col,value in enumerate(values):
                cell = tk.Label(self.benchmark_summary,text=value,bg=WHITE if row%2 else '#edf2ee',
                                fg=INK,font=('Segoe UI',8,'bold' if col in (0,5) else 'normal'),
                                wraplength=105 if col==0 else 55,padx=2,pady=9)
                cell.grid(row=row,column=col,sticky='nsew')
                widgets.append(cell)
            self.benchmark_summary_rows.append(widgets)
        if hasattr(self,'benchmark_table'):
            for item in self.benchmark_table.get_children():
                self.benchmark_table.delete(item)
            for index,result in enumerate(results,1):
                self.benchmark_table.insert('','end',values=(index,result['algorithm'],
                    f"{result['Fácil']:.1f}%",f"{result['Intermedio']:.1f}%",
                    f"{result['Difícil']:.1f}%",f"{result['Extremo']:.1f}%",
                    f"{result['overall']:.1f}%",f"{result['avg_steps']:.1f}",
                    f"{result['avg_operations']:.1f}",f"{result['avg_compute']:.6f}",
                    result['errors'],self.format_date(result['date'])))

    def _difficulty(self):
        p = self.screens['difficulty']
        self.label(p,'Elige tu dificultad',size=24,bold=True).pack(pady=(24,22))
        self.label(p,'¿Qué dificultad te apetece?',bold=True,anchor='w').pack(fill='x',pady=(0,9))
        options = tk.Frame(p,bg=BG)
        options.pack(fill='x')
        options.columnconfigure((0,1),weight=1,uniform='level')
        self.difficulty_buttons = {}
        for index,name in enumerate(('Fácil','Intermedio','Difícil','Extremo')):
            b = Button(options,name,lambda n=name:self.select_difficulty(n),height=62)
            b.grid(row=index//2,column=index%2,sticky='ew',padx=3,pady=3)
            self.difficulty_buttons[name] = b
        self.difficulty_description = self.label(p,'',color=MUTED,justify='left')
        self.difficulty_description.pack(fill='x',pady=12)
        self.home_hint = self.label(p,'',color=MUTED,wraplength=360)
        self.home_hint.pack(pady=(12,6))
        self.generate_button = self.button(p,'Crear mi sudoku  →',self.generate,primary=True,height=54)
        self.cancel_generation_button = self.button(p,'Cancelar generación',self.cancel_generation)
        self.difficulty_back = self.button(p,'Volver',self.go_home)
        self.select_difficulty('Fácil')

    def select_difficulty(self, name):
        if self.generating:
            return
        self.difficulty.set(name)
        self.difficulty_description.config(text=DIFFICULTIES[name])
        for key,button in self.difficulty_buttons.items():
            button.config(text=('✓  ' if key==name else '')+key,selected=key==name)

    def _game(self):
        p = self.screens['game']
        nav = tk.Frame(p,bg=BG)
        nav.pack(fill='x')
        self.back_button = Button(nav,'‹  Inicio',self.go_home,height=38)
        self.back_button.pack(side='left')
        Button(nav,'?  Dificultad',self.report,height=38).pack(side='right')
        self.label(p,'Cada paso cuenta.',size=24,bold=True).pack(pady=(12,4))
        self.puzzle_label = self.label(p,'',size=10,color=MUTED)
        self.puzzle_label.pack(pady=(0,10))
        self.canvas = tk.Canvas(p,width=340,height=340,bg=BG,highlightthickness=0)
        self.canvas.pack(fill='x')
        self.canvas.bind('<Configure>',lambda e:self._board_resize(self.canvas,e))
        self.status = self.label(p,'Elige un algoritmo',bold=True,color=TEAL)
        self.status.pack(pady=(14,4))
        self.reason = self.label(p,'',color=MUTED,wraplength=360)
        self.reason.pack(pady=(0,6))
        self.algorithm = ttk.Combobox(p,state='readonly',values=[cls.name for cls in self.classes])
        self.algorithm.pack(fill='x',pady=(0,6))
        if self.classes:
            self.algorithm.current(0)
        self.algorithm.bind('<<ComboboxSelected>>',lambda e:self.describe())
        self.description = self.label(p,'',size=10,color=MUTED,wraplength=360)
        self.description.pack(fill='x',pady=(0,10))
        self.describe()
        self.run_button = self.button(p,'▶   Ejecutar algoritmo',self.start,primary=True)
        self.pause_button = self.button(p,'Pausar',self.pause,primary=True)
        row = tk.Frame(p,bg=BG)
        row.pack(fill='x')
        row.columnconfigure((0,1),weight=1,uniform='controls')
        self.step_button = Button(row,'Un paso',self.step)
        self.step_button.grid(row=0,column=0,sticky='ew',padx=(0,4))
        self.stop_button = Button(row,'Terminar',self.stop)
        self.stop_button.grid(row=0,column=1,sticky='ew',padx=(4,0))

    def _summary(self):
        p = self.screens['summary']
        self.label(p,'TU RECORRIDO',size=10,color=TEAL,bold=True).pack(pady=(8,8))
        self.summary_title = self.label(p,'',size=25,bold=True)
        self.summary_title.pack()
        self.summary_algorithm = self.label(p,'',color=MUTED,wraplength=350)
        self.summary_algorithm.pack(pady=(6,15))
        self.final_canvas = tk.Canvas(p,width=220,height=220,bg=BG,highlightthickness=0)
        self.final_canvas.pack()
        self.final_canvas.bind('<Configure>',lambda e:self.draw())
        self.score_label = self.label(p,'',size=30,bold=True,color=TEAL)
        self.score_label.pack(pady=(12,0))
        self.summary_metrics = tk.Frame(p,bg=WHITE)
        self.summary_metrics.pack(fill='x',pady=6)
        self.summary_metrics.columnconfigure(1,weight=1)
        self.metric_values = {}
        for row,name in enumerate(('Algoritmo','Fecha y hora','Dificultad','Resultado','Completado','Pasos',
                                    'Operaciones Python','Colocaciones','Tiempo de cálculo','Tiempo total animado')):
            bg = WHITE if row%2==0 else '#edf2ee'
            tk.Label(self.summary_metrics,text=name,bg=bg,fg=MUTED,font=('Segoe UI',10),
                     anchor='w',padx=10,pady=7).grid(row=row,column=0,sticky='nsew')
            value = tk.Label(self.summary_metrics,bg=bg,fg=INK,font=('Segoe UI',10,'bold'),
                             anchor='e',padx=10,pady=7,wraplength=180)
            value.grid(row=row,column=1,sticky='nsew')
            self.metric_values[name] = value
        self.summary_reason = self.label(p,'',size=10,color=MUTED,wraplength=360)
        self.button(p,'Reintentar',self.retry,primary=True)
        self.button(p,'Inicio',self.go_home)
        self.button(p,'Historial de intentos',self.comparison)

    def _board_resize(self, canvas, event):
        desired = min(340,event.width)
        if canvas.winfo_height()!=desired:
            canvas.configure(height=desired)
        self.draw()

    def describe(self):
        i = self.algorithm.current()
        self.description.config(text=self.classes[i].description if i>=0 else 'Añade tu algoritmo en soluciones/ y reinicia.')

    def _controls(self):
        active = self.execution is not None
        self.difficulty_back.config(state='disabled' if self.generating else 'normal')
        self.generate_button.config(state='disabled' if self.generating else 'normal',text='Preparando tu reto…' if self.generating else 'Crear mi sudoku  →')
        for b in self.difficulty_buttons.values():
            b.config(state='disabled' if self.generating else 'normal')
        self.cancel_generation_button.pack_forget()
        if self.generating:
            self.cancel_generation_button.pack(fill='x',after=self.generate_button,pady=4)
        self.run_button.pack_forget()
        self.pause_button.pack_forget()
        button = self.pause_button if active else self.run_button
        button.pack(fill='x',after=self.description,pady=4)
        self.run_button.config(state='normal' if self.board and self.classes else 'disabled')
        self.pause_button.config(text='Continuar' if self.paused else 'Pausar')
        self.step_button.config(state='normal' if self.classes and (not active or self.paused) else 'disabled')
        self.stop_button.config(state='normal' if active else 'disabled')
        self.algorithm.config(state='disabled' if active else 'readonly')
        self.back_button.config(state='normal')
        if hasattr(self,'benchmark_run_button'):
            self.benchmark_run_button.config(state='disabled' if self.benchmark_running or not self.classes else 'normal')
            self.benchmark_algorithm.config(state='disabled' if self.benchmark_running else 'readonly')
            self.benchmark_cancel_button.pack_forget()
            if self.benchmark_running:
                self.benchmark_cancel_button.pack(fill='x',after=self.benchmark_run_button,pady=4)
            self.benchmark_home_button.config(state='disabled' if self.benchmark_running else 'normal')

    def _metrics(self):
        # Las métricas detalladas viven únicamente en el resumen.
        pass

    def render_summary(self, state):
        color = TEAL if state=='Resuelto' else '#b44848'
        self.summary_title.config(text={'Resuelto':'¡Sudoku resuelto!','Sin resolver':'Hasta aquí ha llegado.',
            'Cancelado':'Intento cancelado.','Error':'Intento fallido.'}[state],fg=color)
        self.summary_algorithm.config(text=self.classes[self.algorithm.current()].name+' · '+state)
        s = self.stats
        self.score_label.config(text=f'{score(self.board):.1f}%',fg=color)
        values = (self.classes[self.algorithm.current()].name,self.format_date(self.attempt_date),
                  self.generated.report.level,'Logrado' if state=='Resuelto' else state,f'{score(self.board):.1f}%',
                  s.steps,s.operations,s.placements,f'{s.elapsed_seconds:.6f} s',f'{s.animated_seconds:.2f} s')
        for label,value in zip(self.metric_values.values(),values):
            label.config(text=value)
        self.metric_values['Resultado'].config(fg=color)
        self.summary_reason.pack_forget()
        self.summary_reason.config(text=self.reason.cget('text') if state=='Error' else '')
        if state=='Error':
            self.summary_reason.pack(after=self.summary_metrics,pady=10)
        self.show('summary')

    def go_home(self):
        if self.generating:
            return
        if self.execution:
            self.finish('Cancelado')
        self.board = self.generated = None
        self.highlight = None
        self.show('home')
        self._controls()

    def retry(self):
        if self.board is None:
            return
        self.reset()
        self.show('game')
        self._controls()

    def dialog(self, title):
        window = tk.Toplevel(self.root,bg=BG)
        window.title(title)
        window.geometry('420x380')
        window.transient(self.root)
        window.grab_set()
        body = tk.Frame(window,bg=BG,padx=24,pady=24)
        body.pack(fill='both',expand=True)
        self.label(body,title,size=19,bold=True).pack(pady=(0,16))
        return window,body

    @staticmethod
    def format_date(value):
        return datetime.fromisoformat(value).strftime('%d/%m/%Y %H:%M') if value else '—'

    def comparison(self):
        window,p = self.dialog('Historial de intentos')
        window.geometry(f'{min(1150,self.root.winfo_screenwidth()-100)}x500')
        self.label(p,'Todos los sudokus · más recientes primero',color=MUTED).pack(pady=(0,12))
        columns = ('algorithm','date','difficulty','state','completion','steps','operations','placements','compute','animated')
        holder = tk.Frame(p,bg=BG)
        holder.pack(fill='both',expand=True)
        holder.columnconfigure(0,weight=1)
        holder.rowconfigure(0,weight=1)
        table = ttk.Treeview(holder,columns=columns,show='headings',height=10)
        table.grid(row=0,column=0,sticky='nsew')
        # Only the wide history table has horizontal scrolling; the app itself
        # has no visible side bar. Vertical scrolling is handled by the wheel.
        bar = ttk.Scrollbar(holder,orient='horizontal',command=table.xview)
        bar.grid(row=1,column=0,sticky='ew')
        table.configure(xscrollcommand=bar.set)
        for key,title,width in zip(columns,('Algoritmo','Fecha y hora','Dificultad','Resultado','Completado',
            'Pasos','Operaciones Python','Colocaciones','Cálculo (s)','Total animado (s)'),(220,140,100,110,90,65,125,95,110,135)):
            table.heading(key,text=title)
            table.column(key,width=width,minwidth=width,stretch=False)
        table.tag_configure('success',foreground=TEAL)
        table.tag_configure('failed',foreground='#b44848')
        for r in self.history.all():
            success = r['state']=='Resuelto'
            table.insert('','end',values=(r['algorithm'],self.format_date(r['date']),
                r['difficulty'] or '—','Logrado' if success else r['state'],f"{r['completion']:.1f}%",
                r['steps'],r['operations'],r['placements'],f"{r['compute_seconds']:.6f}",
                f"{r['animated_seconds']:.2f}"),tags=('success' if success else 'failed',))
        self.history_table = table
        self.button(p,'Volver',window.destroy)

    def _benchmark(self):
        p = self.screens['benchmark']
        self.label(p,'Benchmark',size=25,bold=True).pack(pady=(12,5))
        self.label(p,'10 sudokus por dificultad · sin animación',color=MUTED).pack(pady=(0,18))
        self.benchmark_algorithm = ttk.Combobox(p,state='readonly',
            values=['Todos los algoritmos']+[cls.name for cls in self.classes])
        self.benchmark_algorithm.pack(fill='x',pady=(0,8))
        self.benchmark_algorithm.current(0)
        self.benchmark_run_button = self.button(p,'Ejecutar benchmark',self.start_benchmark,primary=True)
        self.benchmark_cancel_button = self.button(p,'Cancelar',self.cancel_benchmark)
        self.benchmark_cancel_button.pack_forget()
        self.benchmark_status = self.label(p,'El conjunto de 40 casos se reutiliza en cada ejecución.',
                                           color=MUTED,justify='center')
        self.benchmark_status.pack(pady=10)
        self.benchmark_progress = ttk.Progressbar(p,mode='determinate',maximum=100)
        self.benchmark_progress.pack(fill='x',pady=(0,15))
        columns = ('rank','algorithm','easy','medium','hard','extreme','overall','steps','operations','time','errors','date')
        holder = tk.Frame(p,bg=BG)
        holder.pack(fill='both',expand=True)
        self.benchmark_table = ttk.Treeview(holder,columns=columns,show='headings',height=9)
        self.benchmark_table.pack(fill='both',expand=True)
        bar = ttk.Scrollbar(holder,orient='horizontal',command=self.benchmark_table.xview)
        bar.pack(fill='x')
        self.benchmark_table.configure(xscrollcommand=bar.set)
        titles = ('#','Algoritmo','Fácil','Intermedio','Difícil','Extremo','Media','Pasos','Operaciones Python','Cálculo s','Errores','Fecha')
        widths = (35,180,80,90,80,80,80,75,130,100,65,125)
        for key,title,width in zip(columns,titles,widths):
            self.benchmark_table.heading(key,text=title)
            self.benchmark_table.column(key,width=width,minwidth=width,stretch=False)
        self.benchmark_home_button = self.button(p,'Inicio',self.go_home)

    def draw(self):
        for canvas in (self.canvas,self.final_canvas):
            canvas.delete('all')
            size = min(canvas.winfo_width(),canvas.winfo_height())
            if size<10:
                continue
            unit = (size-12)/9
            offset = (canvas.winfo_width()-size)/2
            for r in range(9):
                for c in range(9):
                    x,y = offset+6+c*unit,6+r*unit
                    fixed = self.board and (r,c) in self.board.fixed
                    fill = '#d7eee0' if (r,c)==self.highlight else ('#f0f3ee' if fixed else WHITE)
                    canvas.create_rectangle(x,y,x+unit,y+unit,fill=fill,outline='')
                    if self.board and self.board.grid[r][c]:
                        canvas.create_text(x+unit/2,y+unit/2,text=self.board.grid[r][c],fill=INK if fixed else TEAL,
                            font=('Segoe UI',int(unit*.44),'bold' if fixed else 'normal'))
            for i in range(10):
                pos = 6+i*unit
                color = '#7f9690' if i%3==0 else '#dde4de'
                width = 2 if i%3==0 else 1
                canvas.create_line(offset+6,pos,offset+size-6,pos,fill=color,width=width)
                canvas.create_line(offset+pos,6,offset+pos,size-6,fill=color,width=width)
