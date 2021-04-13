# -*- coding: utf-8 -*-
import sys
import os
import functools
import unidecode
import json
from Pyinstaller_util import get_resource_path, get_config_path, get_exe_path, create_path_it_not_exist
from SaveData import SaveData, GeneralInfo, ClientInfo, InvoiceInfo, InvoiceItem
from TemplateGenerator import LatexTemplateGenerator
from invoiceUI import Ui_Dialog
from PySide2.QtWidgets import (QApplication, QMessageBox, QTableWidgetItem,
                               QDialog, QHeaderView, QMenu, QAction)
from PySide2.QtGui import QIcon, QIntValidator
from PySide2.QtCore import QProcess

APP_NAME = "Invoice Generator"
APP_CONFIG_FOLDER = "invoice generator"


class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(get_resource_path(os.path.join('resources', 'noun_Plant.ico'))))
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.lineEdit_invoiceNumber.setValidator(QIntValidator())
        self.ui.progressBar.setMaximum(1)
        self.proc = QProcess()

        self.ui.tableWidget_invoiceContent.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.savePath = create_path_it_not_exist(os.path.join(get_config_path(APP_CONFIG_FOLDER), 'save.json'))
        self.saveData = SaveData(self.savePath)
        self.outputPath = os.path.join(get_exe_path(), create_path_it_not_exist(os.path.join(get_exe_path(), 'output')))
        self.texGenerator = LatexTemplateGenerator(get_resource_path('resources').replace('\\', '/'))

        self.currentGeneralInfo = GeneralInfo()
        self.currentClientInfo = ClientInfo()
        self.currentInvoiceInfo = InvoiceInfo()

        self.ui.pushButton_saveQuickRecallInvoice.clicked.connect(self.save_invoice_info)
        self.ui.pushButton_saveQuickRecallClient.clicked.connect(self.save_client_info)
        self.ui.pushButton_saveQuickRecallGeneral.clicked.connect(self.save_general_info)

        self.ui.comboBox_quickRecallInvoice.activated.connect(self.on_combo_box_invoice_changed)
        self.ui.comboBox_quickRecallClient.activated.connect(self.on_combo_box_client_changed)
        self.ui.comboBox_quickRecallGeneral.activated.connect(self.on_combo_box_general_changed)

        self.ui.pushButton_generateInvoice.clicked.connect(self.generate_invoice)

        self.proc.finished.connect(functools.partial(self._handleProcFinished, self.proc))

        self.ui.toolButton_add.clicked.connect(self.add_row)
        self.ui.toolButton_delete.clicked.connect(self.delete_row)
        self.update_ui()

    def _handleProcFinished(self, process, exitCode):
        stdOut = process.readAllStandardOutput()
        stdErr = process.readAllStandardError()
        print("Standard Out:")
        print(stdOut)
        print("Standard Error:")
        print(stdErr)
        if(exitCode == 0):
            self.success_message('Invoice Generated successfully')
        self.ui.progressBar.setMaximum(1)

    def make_pdf(self, input_folder, input_file):
        if self.proc.isOpen():
            print('cancelled running process')
            self.proc.close()
        self.proc.setWorkingDirectory(input_folder)
        self.proc.start("xelatex", [os.path.join(input_folder, input_file)])
        self.ui.progressBar.setMaximum(0)

    def save_data(self):
        self.save_invoice_info()
        self.save_client_info()
        self.save_general_info()

        if self.saveData.save_client(self.currentClientInfo) and \
                self.saveData.save_invoice(self.currentInvoiceInfo) and \
                self.saveData.save_general(self.currentGeneralInfo):
            self.saveData.save_to_file()
        else:
            self.warning_message("Invalid invoice formatting\n Check for empty or incorrect fields")

    def load_data(self):
        pass

    def list_client(self):
        self.ui.comboBox_quickRecallClient.clear()
        for client in self.saveData.clients:
            self.ui.comboBox_quickRecallClient.addItem(client.name)

    def list_general(self):
        self.ui.comboBox_quickRecallGeneral.clear()
        for general in self.saveData.generals:
            self.ui.comboBox_quickRecallGeneral.addItem(general.company_name)
        pass

    def list_invoice(self):
        self.ui.comboBox_quickRecallInvoice.clear()
        for invoice in self.saveData.invoices:
            self.ui.comboBox_quickRecallInvoice.addItem(invoice.invoice_number)

    def generate_invoice(self):
        print("generating invoice")
        self.save_data()
        filename = ''.join(e for e in unidecode.unidecode(self.currentInvoiceInfo.client.name) if e.isalnum())
        self.texGenerator.render(SaveData.asflatdict(self.currentInvoiceInfo), create_path_it_not_exist(
            os.path.join(self.outputPath, self.currentInvoiceInfo.invoice_number,
                         'Facture_' + self.currentInvoiceInfo.invoice_number + '_' + filename + '.tex')))
        self.make_pdf(os.path.join(self.outputPath, self.currentInvoiceInfo.invoice_number), 'Facture_' + self.currentInvoiceInfo.invoice_number + '_' + filename + '.tex')
        self.update_ui()

    def recall_general_info(self, company_name):
        newGeneral = self.saveData.get_general(company_name)
        self.ui.lineEdit_companyName.setText(newGeneral.company_name)
        self.ui.lineEdit_firstName.setText(newGeneral.first_name)
        self.ui.lineEdit_lastName.setText(newGeneral.last_name)
        self.ui.lineEdit_fullAddress.setText(newGeneral.full_address)
        self.ui.lineEdit_companySIRET.setText(newGeneral.company_siret)
        self.ui.lineEdit_companySIREN.setText(newGeneral.company_siren)
        self.ui.lineEdit_companyAPE.setText(newGeneral.company_ape)
        self.ui.lineEdit_companyEmail.setText(newGeneral.company_email)
        self.ui.lineEdit_companyTelephone.setText(newGeneral.company_phone)
        self.ui.lineEdit_bankIBAN.setText(newGeneral.bank_iban)
        self.ui.lineEdit_bankBIC.setText(newGeneral.bank_bic)

    def recall_client_info(self, name):
        newClient = self.saveData.get_client(name)
        self.ui.lineEdit_clientName.setText(newClient.name)
        self.ui.lineEdit_clientAddressFirst.setText(newClient.address_first_line)
        self.ui.lineEdit_clientAdressSecond.setText(newClient.address_second_line)
        self.update_infos_from_UI()

    def recall_invoice_info(self, invoice_number):
        newInvoice = self.saveData.get_invoice(invoice_number)

        self.ui.lineEdit_invoiceNumber.setText(newInvoice.invoice_number)
        self.ui.lineEdit_invoiceDate.setText(newInvoice.invoice_date)
        self.ui.lineEdit_invoiceName.setText(newInvoice.invoice_name)

        self.ui.tableWidget_invoiceContent.clearContents()
        for item in newInvoice.items:
            row_position = self.ui.tableWidget_invoiceContent.rowCount()
            self.ui.tableWidget_invoiceContent.insertRow(row_position)
            self.ui.tableWidget_invoiceContent.setItem(row_position, 0, QTableWidgetItem(str(item.product_name)))
            self.ui.tableWidget_invoiceContent.setItem(row_position, 1, QTableWidgetItem(str(item.quantity)))
            self.ui.tableWidget_invoiceContent.setItem(row_position, 2, QTableWidgetItem(str(item.price)))

        self.recall_client_info(newInvoice.client.name)
        self.recall_general_info(newInvoice.general.company_name)
        self.update_infos_from_UI()

    def on_combo_box_client_changed(self, index):
        self.recall_client_info(self.ui.comboBox_quickRecallClient.itemText(index))

    def on_combo_box_general_changed(self, index):
        self.recall_general_info(self.ui.comboBox_quickRecallGeneral.itemText(index))

    def on_combo_box_invoice_changed(self, index):
        self.recall_invoice_info(self.ui.comboBox_quickRecallInvoice.itemText(index))

    def save_invoice_info(self):
        self.update_invoice_infos_from_UI()
        if not self.saveData.save_invoice(self.currentInvoiceInfo):
            self.warning_message("Couldn't save new Invoice")
        self.update_ui()

    def save_general_info(self):
        self.update_general_infos_from_UI()
        if not self.saveData.save_general(self.currentGeneralInfo):
            self.warning_message("Couldn't save new General")
        self.update_ui()

    def save_client_info(self):
        self.update_client_infos_from_UI()
        if not self.saveData.save_client(self.currentClientInfo):
            self.warning_message("Couldn't save new Client")
        self.update_ui()

    def add_row(self):
        self.ui.tableWidget_invoiceContent.insertRow(self.ui.tableWidget_invoiceContent.rowCount())

    def delete_row(self):
        self.ui.tableWidget_invoiceContent.removeRow(self.ui.tableWidget_invoiceContent.currentRow())

    def ask_validation(self, text, informative_text, title="Validation Dialog"):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("hey")
        msgBox.setText(text)
        msgBox.setInformativeText(informative_text)
        msgBox.setStandardButtons(QMessageBox.Apply | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec_()
        return True if ret == QMessageBox.Apply else False

    def success_message(self, text):
        ret = QMessageBox.information(self, self.tr("Success"),
                                  self.tr(text),
                                  QMessageBox.Ok,
                                  QMessageBox.Ok)
    def warning_message(self, text):
        ret = QMessageBox.warning(self, self.tr("Warning"),
                                  self.tr(text),
                                  QMessageBox.Ok,
                                  QMessageBox.Ok)

    def update_client_infos_from_UI(self):
        currentClientInfo = ClientInfo()
        currentClientInfo.name = self.ui.lineEdit_clientName.text()
        currentClientInfo.address_first_line = self.ui.lineEdit_clientAddressFirst.text()
        currentClientInfo.address_second_line = self.ui.lineEdit_clientAdressSecond.text()

        self.currentClientInfo = currentClientInfo

    def update_general_infos_from_UI(self):
        currentGeneralInfo = GeneralInfo()
        currentGeneralInfo.company_name = self.ui.lineEdit_companyName.text()
        currentGeneralInfo.first_name = self.ui.lineEdit_firstName.text()
        currentGeneralInfo.last_name = self.ui.lineEdit_lastName.text()
        currentGeneralInfo.full_address = self.ui.lineEdit_fullAddress.text()
        currentGeneralInfo.company_siret = self.ui.lineEdit_companySIRET.text()
        currentGeneralInfo.company_siren = self.ui.lineEdit_companySIREN.text()
        currentGeneralInfo.company_ape = self.ui.lineEdit_companyAPE.text()
        currentGeneralInfo.company_email = self.ui.lineEdit_companyEmail.text()
        currentGeneralInfo.company_phone = self.ui.lineEdit_companyTelephone.text()
        currentGeneralInfo.bank_iban = self.ui.lineEdit_bankIBAN.text()
        currentGeneralInfo.bank_bic = self.ui.lineEdit_bankBIC.text()

        self.currentGeneralInfo = currentGeneralInfo

    def update_invoice_infos_from_UI(self):
        currentInvoiceInfo = InvoiceInfo()
        currentInvoiceInfo.invoice_number = self.ui.lineEdit_invoiceNumber.text()
        currentInvoiceInfo.invoice_date = self.ui.lineEdit_invoiceDate.text()
        currentInvoiceInfo.invoice_name = self.ui.lineEdit_invoiceName.text()
        currentInvoiceInfo.general = self.currentGeneralInfo
        currentInvoiceInfo.client = self.currentClientInfo

        currentInvoiceInfo.items = []
        try:
            for row in range(self.ui.tableWidget_invoiceContent.rowCount()):
                newItem = InvoiceItem()
                newItem.product_name = self.ui.tableWidget_invoiceContent.item(row, 0).text() \
                    if self.ui.tableWidget_invoiceContent.item(row, 0) is not None else ""
                newItem.quantity = int(self.ui.tableWidget_invoiceContent.item(row, 1).text()) \
                    if self.ui.tableWidget_invoiceContent.item(row, 1) is not None else 0
                newItem.price = float(self.ui.tableWidget_invoiceContent.item(row, 2).text()) \
                    if self.ui.tableWidget_invoiceContent.item(row, 2) is not None else 0
                currentInvoiceInfo.items.append(newItem)
        except ValueError:
            self.warning_message("oops Something went wrong, make sure you entered appropriate values")

        self.currentInvoiceInfo = currentInvoiceInfo

    def update_infos_from_UI(self):
        self.update_general_infos_from_UI()
        self.update_client_infos_from_UI()
        self.update_invoice_infos_from_UI()

    def update_ui(self):
        self.list_invoice()
        self.list_client()
        self.list_general()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
