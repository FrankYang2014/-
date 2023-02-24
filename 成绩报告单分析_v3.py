# -*- coding: utf-8 -*-
import datetime
import pathlib
from queue import Queue
from threading import Thread
from tkinter.filedialog import askdirectory
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import utility
import fxv3
# https://ttkbootstrap.readthedocs.io/en/latest/gallery/filesearchengine/
class FileSearchEngine(ttk.Frame):

    queue = Queue()
    searching = False

    def __init__(self, master):
        super().__init__(master, padding=15)
        self.pack(fill=BOTH, expand=YES)

        # application variables
        _path = pathlib.Path().absolute().as_posix()
        self.path_var = ttk.StringVar(value=_path)
        self.term_var = ttk.StringVar(value='')
        self.type_var = ttk.StringVar(value='endswidth')

        # # header and labelframe option container
        option_text = '''1.把需要解析的成绩报告单pdf文件放在一个文件夹下面，文件夹下可设子文件夹，深度不限。
2.科目（一门，不要有错别字，生物多个“学”）：物理、化学、生物学、历史、地理、政治、信息技术、通用技术
3.分析过程中，需加载pdf文件，所需时间较长，请耐心等待。'''
        self.option_lf = ttk.Labelframe(self, text=option_text, padding=15)
        self.option_lf.pack(fill=X, expand=YES, anchor=N)

        self.create_path_row()
        self.create_term_row()
        # self.create_type_row()
        # self.create_results_view()

        # self.progressbar = ttk.Progressbar(
        #     master=self, 
        #     mode=INDETERMINATE, 
        #     bootstyle=(STRIPED, SUCCESS)
        # )
        # self.progressbar.pack(fill=X, expand=YES)

    def create_path_row(self):
        """Add path row to labelframe"""
        path_row = ttk.Frame(self.option_lf)
        path_row.pack(fill=X, expand=YES)
        path_lbl = ttk.Label(path_row, text="Path", width=8)
        path_lbl.pack(side=LEFT, padx=(15, 0))
        path_ent = ttk.Entry(path_row, textvariable=self.path_var)
        path_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        browse_btn = ttk.Button(
            master=path_row, 
            text="选择文件夹", 
            command=self.on_browse, 
            width=10
        )
        browse_btn.pack(side=LEFT, padx=5)

    def create_term_row(self):
        """Add term row to labelframe"""
        term_row = ttk.Frame(self.option_lf)
        term_row.pack(fill=X, expand=YES, pady=15)
        term_lbl = ttk.Label(term_row, text="科目", width=8)
        term_lbl.pack(side=LEFT, padx=(15, 0))
        term_ent = ttk.Entry(term_row, textvariable=self.term_var)
        term_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        search_btn = ttk.Button(
            master=term_row, 
            text="计算", 
            command=self.on_search, 
            bootstyle=OUTLINE, 
            width=8
        )
        search_btn.pack(side=LEFT, padx=5)



    def on_browse(self):
        """Callback for directory browse"""
        path = askdirectory(title="Browse directory")
        if path:
            self.path_var.set(path)


    def on_search(self):
        """Search for a term based on the search type"""
        search_path = self.path_var.get()
        search_term=self.term_var.get()
        
        # search_type = self.type_var.get()

        if search_term is None or len(search_term )==0 or search_term=="":
            print("输入为空")
            return 
        print("开始计算")

        # start search in another thread to prevent UI from locking
        Thread(
            target=fxv3.main, 
            args=(search_path,[search_term]), 
            daemon=True
        ).start()
        
        print("计算完成")
        # self.progressbar.start(10)
        # self.after(100, lambda: self.check_queue(iid))


        

 
       


if __name__ == '__main__':

    app = ttk.Window("学选考成绩报告单分析程序--powered by 杨再兴", "journal")
    FileSearchEngine(app)
    app.mainloop()
