from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
from datetime import datetime
import json
import os


Window.size = (400, 650)
FILE_NAME = "bank_data.json"


class BankApp(App):
    def build(self): return MainScreen()


class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation, self.padding, self.spacing = 'vertical', 10, 10
        self.add_widget(Label(text="🏦 БАНК КИЯНИ", size_hint_y=0.08, font_size=28, bold=True))
        btn = Button(text="➕ СОЗДАТЬ ЯЧЕЙКУ", size_hint_y=0.08, background_color=[0,0.5,1,1])
        btn.bind(on_press=self.create_cell_dialog)
        self.add_widget(btn)
        scroll = ScrollView(size_hint_y=0.76)
        self.cells_grid = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=5)
        self.cells_grid.bind(minimum_height=self.cells_grid.setter('height'))
        scroll.add_widget(self.cells_grid)
        self.add_widget(scroll)
        self.load_cells()


    def load_cells(self):
        self.cells_grid.clear_widgets()
        cells = self.load_data()
        if not cells:
            self.cells_grid.add_widget(Label(text="Нет ячеек. Создайте первую!", size_hint_y=None, height=50, color=[0.5,0.5,0.5,1]))
        else:
            for cell in cells:
                w = CellWidget(cell['name'], cell.get('balance',0), self)
                if cell.get('balance',0) < 0 and len(w.children)>1 and hasattr(w.children[1],'color'):
                    w.children[1].color = [1,0,0,1]
                self.cells_grid.add_widget(w)


    def load_data(self):
        if os.path.exists(FILE_NAME):
            try:
                with open(FILE_NAME,'r',encoding='utf-8') as f:
                    d = json.load(f)
                    if isinstance(d,list):
                        for c in d:
                            if 'history' not in c or not isinstance(c['history'],list): 
                                c['history'] = []
                        return d
            except: pass
        return []


    def save_data(self, cells):
        with open(FILE_NAME,'w',encoding='utf-8') as f:
            json.dump(cells, f, ensure_ascii=False, indent=4)


    def create_cell_dialog(self, _):
        c = BoxLayout(orientation='vertical', spacing=10, padding=10)
        ni = TextInput(hint_text="Введите название ячейки", multiline=False)
        c.add_widget(ni)
        bl = BoxLayout(size_hint_y=0.3, spacing=10)
        d = Popup(title="Создать ячейку", content=c, size_hint=(0.8,0.4))
        def create(_):
            name = ni.text.strip()
            if name:
                cells = self.load_data()
                if not any(cell['name'].lower()==name.lower() for cell in cells):
                    cells.append({'name':name,'balance':0,'history':[]})
                    self.save_data(cells)
                    self.load_cells()
                d.dismiss()
        create_btn = Button(text="СОЗДАТЬ", background_color=[0,0.5,1,1])
        create_btn.bind(on_press=create)
        cancel_btn = Button(text="ОТМЕНА", background_color=[0.7,0.7,0.7,1])
        cancel_btn.bind(on_press=lambda x: d.dismiss())
        bl.add_widget(create_btn)
        bl.add_widget(cancel_btn)
        c.add_widget(bl)
        d.open()


    def open_cell_detail(self, name, balance):
        c = BoxLayout(orientation='vertical', spacing=10, padding=10)
        bl = Label(text=f"[b]{balance}[/b] Кияни", font_size=24, markup=True, size_hint_y=0.1)
        bl.color = [1,0,0,1] if balance<0 else [1,1,1,1]
        c.add_widget(bl)
        tab = BoxLayout(size_hint_y=0.1, spacing=5)
        ob = Button(text="ОПЕРАЦИИ", background_color=[0.3,0.3,0.3,1])
        hb = Button(text="ИСТОРИЯ", background_color=[0.5,0.5,0.5,1])
        tb = Button(text="ПЕРЕВОД", background_color=[0.5,0.5,0.5,1])
        for b in [ob,hb,tb]: tab.add_widget(b)
        c.add_widget(tab)
        ca = BoxLayout(orientation='vertical', size_hint_y=0.7, spacing=10)
        c.add_widget(ca)
        d = Popup(title=f"Ячейка: {name}", content=c, size_hint=(0.95,0.8))


        def show_ops(_):
            ob.background_color, hb.background_color, tb.background_color = [0.3,0.3,0.3,1], [0.5,0.5,0.5,1], [0.5,0.5,0.5,1]
            for cell in self.load_data():
                if cell['name']==name:
                    bl.color = [1,0,0,1] if cell.get('balance',0)<0 else [1,1,1,1]
                    break
            ca.clear_widgets()
            ai = TextInput(hint_text="Сумма", multiline=False, input_filter='int', size_hint_y=0.2)
            ca.add_widget(ai)
            blay = BoxLayout(size_hint_y=0.2, spacing=10)
            
            def dep(_):
                if ai.text and ai.text.isdigit():
                    a = int(ai.text)
                    if a>0:
                        cells = self.load_data()
                        for i,cell in enumerate(cells):
                            if cell['name']==name:
                                if 'history' not in cells[i] or not isinstance(cells[i]['history'],list):
                                    cells[i]['history'] = []
                                cells[i]['balance'] = cell.get('balance',0) + a
                                cells[i]['history'].append({
                                    'type':'💰 Пополнение',
                                    'amount':a,
                                    'balance':cells[i]['balance'],
                                    'time':datetime.now().strftime("%d.%m.%Y %H:%M")
                                })
                                self.save_data(cells)
                                self.load_cells()
                                bl.text = f"[b]{cells[i]['balance']}[/b] Кияни"
                                bl.color = [1,0,0,1] if cells[i]['balance']<0 else [1,1,1,1]
                                break
                        ai.text = ""
            
            def wd(_):
                if ai.text and ai.text.isdigit():
                    a = int(ai.text)
                    if a>0:
                        cells = self.load_data()
                        for i,cell in enumerate(cells):
                            if cell['name']==name:
                                if 'history' not in cells[i] or not isinstance(cells[i]['history'],list):
                                    cells[i]['history'] = []
                                cells[i]['balance'] = cell.get('balance',0) - a
                                cells[i]['history'].append({
                                    'type':'💸 Снятие (долг)',
                                    'amount':a,
                                    'balance':cells[i]['balance'],
                                    'time':datetime.now().strftime("%d.%m.%Y %H:%M")
                                })
                                self.save_data(cells)
                                self.load_cells()
                                bl.text = f"[b]{cells[i]['balance']}[/b] Кияни"
                                bl.color = [1,0,0,1] if cells[i]['balance']<0 else [1,1,1,1]
                                break
                        ai.text = ""
            
            db = Button(text="💰 ПОПОЛНИТЬ", background_color=[0.2,0.6,0.2,1])
            wb = Button(text="💸 СНЯТЬ", background_color=[0.8,0.5,0,1])
            db.bind(on_press=dep)
            wb.bind(on_press=wd)
            blay.add_widget(db)
            blay.add_widget(wb)
            ca.add_widget(blay)


        def show_hist(_):
            ob.background_color, hb.background_color, tb.background_color = [0.5,0.5,0.5,1], [0.3,0.3,0.3,1], [0.5,0.5,0.5,1]
            for cell in self.load_data():
                if cell['name']==name:
                    bl.color = [1,0,0,1] if cell.get('balance',0)<0 else [1,1,1,1]
                    break
            ca.clear_widgets()
            hist = []
            for cell in self.load_data():
                if cell['name']==name:
                    h = cell.get('history',[])
                    hist = h if isinstance(h,list) else []
                    break
            hs = ScrollView(size_hint_y=1)
            hg = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=5)
            hg.bind(minimum_height=hg.setter('height'))
            if not hist:
                hg.add_widget(Label(text="Нет операций", size_hint_y=None, height=50, color=[0.5,0.5,0.5,1]))
            else:
                for op in reversed(hist[-20:]):
                    t = op.get('time','00.00.0000 00:00')
                    ot = op.get('type','Операция')
                    a = op.get('amount',0)
                    bal = op.get('balance',0)
                    hg.add_widget(Label(
                        text=f"{t}  {ot}  {a} Кияни  (Баланс: {bal})",
                        size_hint_y=None, height=40, halign='left', valign='middle',
                        text_size=(d.width-30, None)
                    ))
            hs.add_widget(hg)
            ca.add_widget(hs)


        def show_trans(_):
            ob.background_color, hb.background_color, tb.background_color = [0.5,0.5,0.5,1], [0.5,0.5,0.5,1], [0.3,0.3,0.3,1]
            for cell in self.load_data():
                if cell['name']==name:
                    bl.color = [1,0,0,1] if cell.get('balance',0)<0 else [1,1,1,1]
                    break
            ca.clear_widgets()
            cells = self.load_data()
            oc = [c for c in cells if c['name']!=name]
            if not oc:
                l = Label(
                    text="😕 У вас только одна ячейка\n\nСоздайте еще хотя бы одну ячейку для перевода",
                    size_hint_y=0.3, color=[0.5,0.5,0.5,1], halign='center', valign='middle'
                )
                l.bind(size=l.setter('text_size'))
                ca.add_widget(l)
                return
            
            l = Label(text="Кому перевести:", size_hint_y=0.1, halign='left', valign='middle')
            l.bind(size=l.setter('text_size'))
            ca.add_widget(l)
            
            rs = BoxLayout(size_hint_y=0.15, spacing=5)
            ri = TextInput(hint_text="Имя ячейки", multiline=False, size_hint_x=0.6)
            ri.text = oc[0]['name'].strip()
            rs.add_widget(ri)
            bp = Button(text="◀", size_hint_x=0.2)
            bn = Button(text="▶", size_hint_x=0.2)
            ci = 0
            
            def prev(_):
                nonlocal ci
                cc = self.load_data()
                co = [c for c in cc if c['name']!=name]
                if not co: 
                    ri.text = ""
                    return
                if ci >= len(co): 
                    ci = len(co)-1
                ci -= 1
                if ci < 0: 
                    ci = len(co)-1
                ri.text = co[ci]['name'].strip()
            
            def nxt(_):
                nonlocal ci
                cc = self.load_data()
                co = [c for c in cc if c['name']!=name]
                if not co: 
                    ri.text = ""
                    return
                if ci >= len(co): 
                    ci = 0
                ci = (ci+1) % len(co)
                ri.text = co[ci]['name'].strip()
            
            bp.bind(on_press=prev)
            bn.bind(on_press=nxt)
            rs.add_widget(bp)
            rs.add_widget(bn)
            ca.add_widget(rs)
            
            ca.add_widget(Label(text="Сумма перевода:", size_hint_y=0.1, halign='left'))
            ai = TextInput(hint_text="Сумма", multiline=False, input_filter='int', size_hint_y=0.15)
            ca.add_widget(ai)
            
            def tr(_):
                if ai.text and ai.text.isdigit():
                    a = int(ai.text)
                    rn = ri.text.strip()
                    if a>0 and rn:
                        cells = self.load_data()
                        si = ri2 = -1
                        for i,c in enumerate(cells):
                            if c['name'] == name: 
                                si = i
                            if c['name'].lower() == rn.lower(): 
                                ri2 = i
                        
                        if si != -1 and ri2 != -1 and si != ri2:
                            sb = cells[si].get('balance',0)
                            if sb >= a:
                                if 'history' not in cells[si] or not isinstance(cells[si]['history'],list):
                                    cells[si]['history'] = []
                                if 'history' not in cells[ri2] or not isinstance(cells[ri2]['history'],list):
                                    cells[ri2]['history'] = []
                                
                                cells[si]['balance'] = sb - a
                                t = datetime.now().strftime("%d.%m.%Y %H:%M")
                                cells[si]['history'].append({
                                    'type':'📤 Перевод',
                                    'amount':a,
                                    'to':rn,
                                    'balance':cells[si]['balance'],
                                    'time':t
                                })
                                
                                cells[ri2]['balance'] = cells[ri2].get('balance',0) + a
                                cells[ri2]['history'].append({
                                    'type':'📥 Перевод',
                                    'amount':a,
                                    'from':name,
                                    'balance':cells[ri2]['balance'],
                                    'time':t
                                })
                                
                                self.save_data(cells)
                                self.load_cells()
                                bl.text = f"[b]{cells[si]['balance']}[/b] Кияни"
                                bl.color = [1,0,0,1] if cells[si]['balance']<0 else [1,1,1,1]
                                ai.text = ""
                                
                                p = Popup(
                                    title="✅ Успешно",
                                    content=Label(text=f"Переведено {a} Кияни\nв ячейку {rn}"),
                                    size_hint=(0.7,0.3)
                                )
                                p.open()
                                Clock.schedule_once(lambda dt: p.dismiss(), 2)
                            else:
                                p = Popup(
                                    title="❌ Ошибка",
                                    content=Label(text="Недостаточно средств"),
                                    size_hint=(0.7,0.3)
                                )
                                p.open()
                                Clock.schedule_once(lambda dt: p.dismiss(), 2)
                        else:
                            p = Popup(
                                title="❌ Ошибка",
                                content=Label(text="Нельзя перевести самому себе\nили ячейка не найдена"),
                                size_hint=(0.7,0.3)
                            )
                            p.open()
                            Clock.schedule_once(lambda dt: p.dismiss(), 2)
            
            transfer_btn = Button(text="💱 ПЕРЕВЕСТИ", size_hint_y=0.15, background_color=[0.5,0,0.5,1])
            transfer_btn.bind(on_press=tr)
            ca.add_widget(transfer_btn)


        ob.bind(on_press=show_ops)
        hb.bind(on_press=show_hist)
        tb.bind(on_press=show_trans)
        show_ops(None)
        
        cb = Button(text="ЗАКРЫТЬ", size_hint_y=0.08, background_color=[0.5,0.5,0.5,1])
        cb.bind(on_press=lambda x: d.dismiss())
        c.add_widget(cb)
        d.open()


class CellWidget(BoxLayout):
    def __init__(self, name, balance, ms, **kwargs):
        super().__init__(**kwargs)
        self.name, self.main_screen = name, ms
        self.size_hint_y, self.height, self.spacing, self.padding = None, 60, 5, 5
        self.add_widget(Label(text=f"[b]{name}[/b]", size_hint_x=0.4, markup=True))
        bc = [1,0,0,1] if balance<0 else [1,1,1,1]
        self.add_widget(Label(text=f"{balance} Кияни", size_hint_x=0.3, color=bc))
        b = Button(text="ОТКРЫТЬ", size_hint_x=0.3, background_color=[0.2,0.6,0.2,1])
        b.bind(on_press=self.open_cell)
        self.add_widget(b)
    
    def open_cell(self, _):
        cells = self.main_screen.load_data()
        if cells:
            for c in cells:
                if c['name'] == self.name:
                    self.main_screen.open_cell_detail(self.name, c.get('balance',0))
                    return
        self.main_screen.open_cell_detail(self.name, 0)


if __name__ == '__main__':
    BankApp().run()
