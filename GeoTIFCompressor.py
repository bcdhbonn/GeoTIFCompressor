#Command to make Exe - run from Anaconda Terminal
#auto-py-to-exe

#import all necessary moduls
#from cmath import e
import os
import sys
import glob
#import time
#from types import LambdaType
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QTimer, QPropertyAnimation, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QDesktopWidget, QGridLayout, QMainWindow, QVBoxLayout, QWidget, QInputDialog, QFileDialog, QLabel, QProgressBar, QMessageBox
from qtwidgets import Toggle, AnimatedToggle
import qdarktheme

#check if GDAL is installed
try:
    from osgeo import ogr, osr, gdal
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')

#basedir for ico
basedir = os.path.dirname(__file__)
outputdir = ""
#variables for compress
orthos =[]
nearblacks =[]
comps = []

#creates own icon in taskbar
try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'BCDH.Kompressor.version.1'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

class MainWindow(QMainWindow):
    
    #Init Window
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeoTIF Compressor")#Name
        #self.setFixedWidth(600)#Size X
        #self.setFixedHeight(380)#Size Y
        self.layout()#Layout
        self.initRecenter()#def Recenter
   
    #recenter window
    def initRecenter(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        
    #layout 
    def layout(self):
        widget = QWidget()
        layout = QGridLayout()

        ##############  IMPORT & EXPORT ##############
        #Input Path
        self.importbtn = QPushButton('Import', self)
        self.importbtn.clicked.connect(self.input_path)
        self.importbtn.setFont(QFont('Times', 15))

        #Output Path
        self.outputbtn = QPushButton('Output Folder', self)
        self.outputbtn.clicked.connect(self.output_path)
        self.outputbtn.setFont(QFont('Times', 15))
        self.outputbtn.setEnabled(False)
       
        #Label Path
        self.outputPathText = QLabel()
        self.outputPathText.setText("Output Folder:")
        self.outputPathText.setFont(QFont('Times', 9))
        self.outputPathText.setStyleSheet("color: black; background-color: lightgray")

        ##############  OPTIONS ##############
        #Label for Options
        self.optionsText = QLabel()
        self.optionsText.setText("Options:")
        self.optionsText.setFont(QFont('Times', 13))
        
        #Label for overwrite-Option
        self.overwriteOption = QLabel()
        self.overwriteOption.setText("Overwrite existing GeoTIFs:")
        self.overwriteOption.setFont(QFont('Times', 10))

        #Toggle toggle_overwrite
        MainWindow.toggle_overwrite = Toggle()
        MainWindow.toggle_overwrite.setFixedSize(QtCore.QSize(80, 50))
        MainWindow.toggle_overwrite.stateChanged.connect(self.overwrite_switch)

        #Label for InputAsOutputText-Option
        self.InputAsOutputText = QLabel()
        self.InputAsOutputText.setText("Use Import-Path as Output-Path:")
        self.InputAsOutputText.setFont(QFont('Times', 10))

        #Toggle toggle_outputdir
        MainWindow.toggle_outputdir = Toggle()
        MainWindow.toggle_outputdir.stateChanged.connect(self.output_switch)
        MainWindow.toggle_outputdir.setFixedSize(QtCore.QSize(80, 50))

        #Label for Pyramid-Option
        self.pyramidOption = QLabel()
        self.pyramidOption.setText("Create Image Pyramids:")
        self.pyramidOption.setFont(QFont('Times', 10))

        #Toggle toggle_pyramidOption
        MainWindow.toggle_pyramidOption = Toggle()
        MainWindow.toggle_pyramidOption.setFixedSize(QtCore.QSize(80, 50))

        ##############  Compress ##############
        #Compress Data
        self.compressbtn = QPushButton('Compress', self)
        self.compressbtn.clicked.connect(self.onStartProgressbar)
        self.compressbtn.setFont(QFont('Times', 15))
        self.compressbtn.setEnabled(False)

        ##############  Progressbar ##############
        #Progressbar
        self.progress = QProgressBar(self)
        self.progress.setRange(0,1)
        
        ##############  WorkerThread ##############
        self.worker = WorkerThread()
        self.worker.taskFinished.connect(self.onFinishedProgressBar)

        ##############  Layout ##############
        #add Widet in GridLayout
        layout.addWidget(self.importbtn,0,0,1,1)
        layout.addWidget(self.outputbtn,0,1,1,1)
        layout.addWidget(self.outputPathText, 1,0,1,2)

        layout.addWidget(self.optionsText,2,0,1,1)
        
        layout.addWidget(self.overwriteOption,3,0,1,1)
        layout.addWidget(MainWindow.toggle_overwrite,3,1,1,1)

        layout.addWidget(self.InputAsOutputText,4,0,1,1)
        layout.addWidget(MainWindow.toggle_outputdir,4,1,1,1)

        layout.addWidget(self.pyramidOption,5,0,1,1)
        layout.addWidget(MainWindow.toggle_pyramidOption,5,1,1,1)
        
        layout.addWidget(self.compressbtn,6,0,1,2)
        layout.addWidget(self.progress,7,0,1,2)

        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    #Input Data
    def input_path(self):
        #File Dialog
        orthos.clear()
        global outputdir
        outputdir = ""
        filename, _ = QFileDialog.getOpenFileNames(self, "Import Orthos", "", "GeoTIFs (*.tif)")
        if filename:
            for i in range(len(filename)):
                #append Orthos to List
                orthos.append(filename[i])
                print("InputData")
                print("".join(["Loaded: ",str(len(filename))]))
                #set Button Text from loaded
                self.importbtn.setText("".join(["GeoTIFs: ",str(len(filename))]))
                self.outputbtn.setEnabled(True)
        if not orthos:
            self.importbtn.setText("Import")
            self.compressbtn.setEnabled(False)
            self.outputbtn.setEnabled(False)
            MainWindow.toggle_overwrite.setChecked(False)
            MainWindow.toggle_outputdir.setChecked(False)
            MainWindow.toggle_pyramidOption.setChecked(False)
            self.outputPathText.setText("Output Folder: ")
                
    #Set Output Path
    def output_path(self):
        global outputdir
        outputdir = ""
        #Open Explorer to define Folder
        outputdir = QFileDialog.getExistingDirectory(self,"Export Path")
        if outputdir:
            self.outputPathText.setText("".join(["Output Folder: ",outputdir,"/"]))
            outputdir = "".join([outputdir,"/"])
            self.compressbtn.setEnabled(True)
        else:
            self.outputPathText.setText("Output Folder: ")
            outputdir = ""
            self.compressbtn.setEnabled(False)
        print(outputdir)
        
          
    #overwrite existing GeoTIFs
    def overwrite_switch(self):
        if MainWindow.toggle_overwrite.isChecked():
            #disable button for output
            self.outputbtn.setEnabled(False)
            #enable swtich for outputdir
            MainWindow.toggle_outputdir.setChecked(True)
        else:
            #enable button for output
            self.outputbtn.setEnabled(True)
            #disable swtich for outputdir
            MainWindow.toggle_outputdir.setChecked(False)
    
    #Switch: sets Input-Path as Output-Path
    def output_switch(self):
        global outputdir
        outputdir = ""
        if MainWindow.toggle_outputdir.isChecked():
            #set Input as Output - use first Ortho from list
            try:
                outputdir = "".join([os.path.dirname(orthos[0]),"/"])
                self.outputPathText.setText("".join(["Output Folder: ",outputdir]))
                self.compressbtn.setEnabled(True)
            except:
                MainWindow.toggle_outputdir.setCheckState(False)
                if MainWindow.toggle_overwrite.isChecked():
                    MainWindow.toggle_overwrite.setCheckState(False)
                QMessageBox.information(self, "Error!","Import GeoTIFs first!")
            print(outputdir)
            #disable button for output
            self.outputbtn.setEnabled(False)
        else:
            #enable button for output
            self.outputbtn.setEnabled(True)
            self.compressbtn.setEnabled(False)
            self.outputPathText.setText("".join(["Output Folder: ",outputdir]))
     
    #Start Worker for compression
    def onStartProgressbar(self):
        self.progress.setRange(0,0)
        #starts compression
        self.worker.start()

    def onFinishedProgressBar(self):
        global done
        #reset outputdir and ortho array
        global outputdir
        outputdir = ""
        orthos.clear()
        nearblacks.clear()
        comps.clear()
        # Stop the pulsation
        self.progress.setRange(0,1)
        #Message compression is done
        QMessageBox.information(self, "Completed!","Compression completed!")
        #Reset everything
        self.outputPathText.setText("Output Folder: ")
        self.importbtn.setText("Import")
        self.compressbtn.setEnabled(False)
        MainWindow.toggle_overwrite.setChecked(False)
        MainWindow.toggle_outputdir.setChecked(False)
        MainWindow.toggle_pyramidOption.setChecked(False)
        self.outputbtn.setEnabled(False)
        
        
#Class for Compression
class WorkerThread(QThread):
    taskFinished = QtCore.pyqtSignal()
    def run(self):
        global outputdir
        global done
        
        #Settings
        gdal.SetConfigOption('GDAL_TIFF_INTERNAL_MASK', 'YES')
        gdal.SetConfigOption("COMPRESS_OVERVIEW", "DEFLATE")

        #GdalNearblack
        print("nearblack GO")
        for i in range(len(orthos)):
            customPathNearblack = outputdir
            outputNameNearblack = "".join([os.path.basename(orthos[i])[:-4], "_nearblack.tif"])
            outputArgumentNearblack = "".join([customPathNearblack, outputNameNearblack])
            gdal.Nearblack(outputArgumentNearblack,orthos[i],options="-co TILED=YES -of Gtiff -white -nb 2 -near 15 -setalpha")
        print("nearblack DONE")

        #get nearblacks
        os.chdir(outputdir)
        for file in glob.glob("*_nearblack.tif"):
            nearblacks.append(file)

        print("GdalTranslate GO")
        #GdalTranslate
        for i in range(len(nearblacks)):
             customPathTranslate = outputdir
             outputNameTranslate = "".join([os.path.basename(nearblacks[i])[:-14], "_Comp.tif"])
             outputArgumentTranslate = "".join([customPathTranslate, outputNameTranslate])
             if MainWindow.toggle_overwrite.isChecked():
                 gdal.Translate(orthos[i],nearblacks[i],options="-of Gtiff -b 1 -b 2 -b 3 -mask 4 -co COMPRESS=JPEG -co TILED=YES -co PHOTOMETRIC=YCBCR")
             else:
                 gdal.Translate(outputArgumentTranslate,nearblacks[i],options="-of Gtiff -b 1 -b 2 -b 3 -mask 4 -co COMPRESS=JPEG -co TILED=YES -co PHOTOMETRIC=YCBCR")
            
        print("GdalTranslate DONE")
        #Remove Nearblack
        for i in range(len(nearblacks)):
            try:
                os.remove(nearblacks[i])
            except:
                print("Cant find Nearblacks")

        #get comps
        os.chdir(outputdir)
        if MainWindow.toggle_overwrite.isChecked():
            comps = orthos
            print(comps)
        else:
            comps = []
            for i in range(len(orthos)):
                comps.append("".join([os.path.basename(orthos[i])[:-4], "_Comp.tif"]))
                print(comps[i])
            print(comps)
        
        #Build Pyramids 
        if MainWindow.toggle_pyramidOption.isChecked():
            print("Pyramids GO")
            for i in range(len(comps)):
                Image = gdal.Open(comps[i], 1)
                Image.BuildOverviews("AVERAGE", [2,4,8,16])
            print("Pyramids DONE")
        print("COMPRESSION DONE")
        #emits when process done
        self.taskFinished.emit()
                
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)  
    qdarktheme.setup_theme()
    app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, 'BCDH.ico')))
    mainWin  = MainWindow()
    mainWin .show()
    app.exec()