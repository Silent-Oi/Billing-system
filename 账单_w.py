from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton,  QPlainTextEdit,QMessageBox,QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
import json,time,csv,sys

#定义类
class Bill():

    def __init__(self):

        #读取ui文件
        qfile_stats=QFile('E:/Silence/OneDrive - gsyw/Work/computer/python/ui/bill.ui')
        qfile_stats.open(QFile.ReadOnly)
        qfile_stats.close()

        #实例
        self.ui=QUiLoader().load(qfile_stats)
        self.ui.plainTextEdit.setPlaceholderText(time.strftime('%Y/%m/%d, %H:%M:%S, %A')+"\n欢迎使用账单系统")      #默认显示内容

        #点击按钮时的操作
        self.ui.button1.clicked.connect(self.write)     #记录
        self.ui.button2.clicked.connect(self.read)      #显示当月所有记录 
        self.ui.button3.clicked.connect(self.find)      #查询
        self.ui.button4.clicked.connect(self.dele)      #删除最新记录
        self.ui.pathchoice.clicked.connect(self.pathc)  #选择文件
        
    def pathc(self):         #选择账单文件
        
        #记录账单文件路径到python
        file_path=QFileDialog.getOpenFileName(self.ui,'选择账单文件','./','All files( * )')
        with open('E:/Silence/OneDrive - gsyw/Work/computer/python/misc/账单/config.json','w') as f:
            json.dump(file_path,f)  
        
        #执行显示路径和统计
        self.showpath()
        self.DM()

    def showpath(self):      #显示选择的账单文件
        with open('E:/Silence/OneDrive - gsyw/Work/computer/python/misc/账单/config.json','r') as f:
            path=json.load(f)
        self.ui.pathshow.setText(path[0])

    def write(self):        #写入新纪录

        #读取账单文件
        with open('E:/Silence/OneDrive - gsyw/Work/computer/python/misc/账单/config.json','r') as f:                    #读取路径
            path=json.load(f)[0]        
        with open('{}'.format(path), "r") as read_file:                                                                 #读取文件
            data = list(csv.reader(read_file))                                                                          #将账单内容存为列表
        with open('E:/Silence/OneDrive - gsyw/Work/computer/python/misc/账单/2023bill_back.csv','w',newline='') as f:   #备份
            writer=csv.writer(f)
            writer.writerows(data)

        #定义初始变量
        day=str(time.strftime('%Y/%m/%d'))      #完整日期，直接存入新纪录
        day_d=str(time.strftime('%d'))          #当日日期
        day_m=str(time.strftime('%m'))          #当月月份

        #读取输入框内的信息
        money=str(self.ui.moneyin.text())       #金额
        sort=str(self.ui.sortin.currentText())  #种类
        event=str(self.ui.eventin.toPlainText())#描述

        if (money or event)=='':                #防止误记录
            self.ui.plainTextEdit.setPlainText('--------\n记录失败\n--------')
        else:
            money=float(money)
            data.append([day,sort,money,event,day_m,day_d])                 #添加记录到data
            self.ui.plainTextEdit.setPlainText('--------\n记录成功\n--------')
            with open('{}'.format(path),'w',newline='') as f:               #将data保存
                writer=csv.writer(f)
                writer.writerows(data)

    def read(self):         #读取当月记录

        with open('E:/Silence/OneDrive - gsyw/Work/computer/python/misc/账单/config.json','r') as f:    #读取路径
            path=json.load(f)[0]
        with open('{}'.format(path), "r") as read_file:                                                 #读取文件
            data = list(csv.reader(read_file))

        #定义初始变量
        data2=data[1:]                  #去除首行
        data3=[]                        #空列表，为了后面输出显示
        day_d=str(time.strftime('%d'))  #当日日期
        day_m=str(time.strftime('%m'))  #当月月份
        total_d=0                       #当日总支出
        total_m=0                       #当月总支出
        i2=0                            #循环变量
        block='            '            #12位空格字符串

        for row in data2:
            if float(row[-2])==float(day_m):                                                #判断记录是否为当月，如果是就把记录添加到data3末尾并且计算月总支出
                data3.append('{:<12}{:<7}￥{:<8}{}'.format(row[0],row[1],row[2],row[3])) 
                total_m+=float(row[2])                                                      
                if str(row[-1])==day_d:                                                     #判断是否为当日，如果是就计算日总支出
                    total_d+=float(row[2])
        
        #把日期连续的记录除了第一个记录以外的日期替换为空格
        for i in range(1,len(data3)):                                                       
            if data3[i][0:11]==data3[i2][0:11]:
                data3[i]=block+data3[i][12:]
            else:
                i2=i

        #输出显示
        self.ui.money_d.setText('日支出:'+str(total_d)+'元')
        self.ui.money_m.setText('月支出:'+'{0:.1f}'.format(total_m)+'元')
        self.ui.plainTextEdit.setPlainText('\n'.join(data3))

    def dele(self):         #删除最新记录
        with open('E:/Silence/OneDrive - gsyw/Work/computer/python/misc/账单/config.json','r') as f: #读取路径
            path=json.load(f)[0]

        choice = QMessageBox.question(
        self.ui,
        '删除确认',
        '确定要删除最新的一条记录吗？',
        QMessageBox.No,QMessageBox.Yes)         #把yes和no选项互换，防止windows把鼠标默认移动到yes导致误删除

        if choice == QMessageBox.No:
            self.ui.plainTextEdit.setPlainText('操作取消')

        if choice == QMessageBox.Yes:
            with open('{}'.format(path), "r") as read_file:                                                                 #读取文件
                data = list(csv.reader(read_file))
            with open('E:/Silence/OneDrive - gsyw/Work/computer/python/misc/账单/2023bill_back.csv','w',newline='') as f:   #备份
                writer=csv.writer(f)
                writer.writerows(data)
            
            data.pop()                                          #删除
            with open('{}'.format(path),'w',newline='') as f:   #保存
                writer=csv.writer(f)
                writer.writerows(data)
            self.ui.plainTextEdit.setPlainText('删除成功')

    def find(self):
        with open('E:/Silence/OneDrive - gsyw/Work/computer/python/misc/账单/config.json','r') as f:
            path=json.load(f)[0]
        with open('{}'.format(path), "r") as read_file: #读取事件
            data = list(csv.reader(read_file))
        header=data[0]
        data2=data[1:]
        data3=[]
        total=0
        month_f=str(self.ui.findmonth.currentText())
        sort_f=str(self.ui.findsort.currentText())
        i2=0
        block='            '
        if sort_f=='全部':
            for row in data2:
                if float(row[-2])==float(month_f):
                    data3.append('{:<12}{:<7}￥{:<8}{}'.format(row[0],row[1],row[2],row[3]))
                    total+=float(row[2])
            for i in range(1,len(data3)):
                if data3[i][0:11]==data3[i2][0:11]:
                    data3[i]=block+data3[i][12:]
                else:
                    i2=i
            self.ui.money_m.setText(str(month_f)+'月支出:'+'{0:.1f}'.format(total)+'元')
            self.ui.plainTextEdit.setPlainText('\n'.join(data3))
        else:
            for row in data2:
                if float(row[-2])==float(month_f):
                    if str(row[1])==str(sort_f):
                        data3.append('{:<12}{:<7}￥{:<8}{}'.format(row[0],row[1],row[2],row[3]))
                        total+=float(row[2])
            for i in range(1,len(data3)):
                if data3[i][0:11]==data3[i2][0:11]:
                    data3[i]=block+data3[i][12:]
                else:
                    i2=i
            self.ui.money_m.setText(str(month_f)+'月'+str(sort_f)+'支出:'+'{0:.1f}'.format(total)+'元')
            self.ui.plainTextEdit.setPlainText('\n'.join(data3))

    def DM(self):
        with open('E:/Silence/OneDrive - gsyw/Work/computer/python/misc/账单/config.json','r') as f:
            path=json.load(f)[0]
        with open('{}'.format(path), "r") as read_file: #读取事件
            data = list(csv.reader(read_file))
        data2=data[1:]
        day_d=str(time.strftime('%d'))
        day_m=str(time.strftime('%m'))
        total=0
        total_d=0
        total_m=0
        for row in data2:
            total+=float(row[2])
            if float(row[-2])==float(day_m):
                total_m+=float(row[2])
                if str(row[-1])==day_d:
                    total_d+=float(row[2])
        self.ui.money_d.setText('日支出:'+str(total_d)+'元')
        self.ui.money_m.setText('月支出:'+'{0:.1f}'.format(total_m)+'元')
        self.ui.money_a.setText('{0:.1f}'.format(total)+'元')

app = QApplication([])
bill2023 = Bill()
bill2023.ui.show()
bill2023.DM()
bill2023.showpath()
app.exec_()
