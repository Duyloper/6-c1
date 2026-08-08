import sys, os, shutil, json
from datetime import datetime
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox, QLabel, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

def lay_duong_dan_nguoi_dung(ten_dang_nhap, ten_file):
    """Lấy đường dẫn tới 1 file JSON cụ thể bên trong thư mục riêng của người dùng, tạo thư mục nếu chưa có"""
    thu_muc_nguoi_dung = os.path.join(THU_MUC_CSDL, ten_dang_nhap)  # Thư mục riêng của người dùng
    os.makedirs(thu_muc_nguoi_dung, exist_ok=True)  # Tạo thư mục nếu chưa có
    return os.path.join(thu_muc_nguoi_dung, ten_file)  # Trả về đường dẫn đầy đủ tới file cần dùng

THU_MUC_CSDL = os.path.dirname(os.path.abspath(__file__))  # Đường dẫn tuyệt đối tới thư mục chứa file main.py (thư mục gốc của dự án)

def lay_duong_dan_giao_dien(tap_tin):
    """Lấy đường dẫn tuyệt đối tới file giao diện (.ui)"""
    return os.path.join(THU_MUC_CSDL, tap_tin)  # Nối đường dẫn thư mục gốc với tên file giao diện để được đường dẫn đầy đủ

def dat_chu_dam(doi_tuong, danh_sach_nhan):
    chu = QFont()
    chu.setBold(True)
    for ten_nhan in danh_sach_nhan:
        if hasattr(doi_tuong, ten_nhan):
            getattr(doi_tuong, ten_nhan).setFont(chu)

TY_LE_HIEN_TAI = {"gia_tri": 1.0}

def gan_co_gian(cua_so, chieu_rong_goc, chieu_cao_goc):
    cua_so._kich_thuoc_goc = (chieu_rong_goc, chieu_cao_goc)
    cua_so._danh_sach_widget_co_gian = []
    cua_so._dang_xu_ly_thay_doi_kich_thuoc = False
    cua_so.setMinimumSize(chieu_rong_goc, chieu_cao_goc)
    cua_so.setWindowFlags(cua_so.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
    ty_le_dau = max(TY_LE_HIEN_TAI["gia_tri"], 1.0)
    cua_so.resize(int(chieu_rong_goc * ty_le_dau), int(chieu_cao_goc * ty_le_dau))

    for widget_con in cua_so.findChildren(QWidget):
        _ghi_nho_widget(cua_so, widget_con)

    resize_goc = cua_so.resizeEvent

    def resize_event_moi(su_kien):
        if resize_goc:
            resize_goc(su_kien)

        if cua_so._dang_xu_ly_thay_doi_kich_thuoc:
            ap_dung_co_gian(cua_so)
            return

        chieu_rong, chieu_cao = cua_so._kich_thuoc_goc
        if chieu_rong <= 0 or chieu_cao <= 0:
            return
        ty_le = max(cua_so.width() / chieu_rong, cua_so.height() / chieu_cao, 1.0)
        man_hinh = QApplication.primaryScreen().availableGeometry() if QApplication.primaryScreen() else None
        if man_hinh:
            ty_le = min(ty_le, man_hinh.width() / chieu_rong, man_hinh.height() / chieu_cao)
        chieu_rong_moi = int(chieu_rong * ty_le)
        chieu_cao_moi = int(chieu_cao * ty_le)
        if chieu_rong_moi != cua_so.width() or chieu_cao_moi != cua_so.height():
            cua_so._dang_xu_ly_thay_doi_kich_thuoc = True
            cua_so.resize(chieu_rong_moi, chieu_cao_moi)
            cua_so._dang_xu_ly_thay_doi_kich_thuoc = False
        ap_dung_co_gian(cua_so)
        TY_LE_HIEN_TAI["gia_tri"] = ty_le

    cua_so.resizeEvent = resize_event_moi

def _ghi_nho_widget(cua_so, widget):
    chu = widget.font()
    diem = chu.pointSizeF() if chu.pointSizeF() > 0 else float(chu.pointSize())
    toa_do = widget.geometry()
    cua_so._danh_sach_widget_co_gian.append({
        "widget": widget,
        "x": toa_do.x(), "y": toa_do.y(),
        "r": toa_do.width(), "c": toa_do.height(),
        "pt": max(diem, 0.0),
    })

def ap_dung_co_gian(cua_so):
    if not hasattr(cua_so, "_kich_thuoc_goc"):
        return
    chieu_rong_goc, chieu_cao_goc = cua_so._kich_thuoc_goc
    if chieu_rong_goc <= 0 or chieu_cao_goc <= 0:
        return
    ty_le = min(cua_so.width() / chieu_rong_goc, cua_so.height() / chieu_cao_goc)
    for thong_tin in cua_so._danh_sach_widget_co_gian:
        widget = thong_tin["widget"]
        try:
            widget.setGeometry(
                int(thong_tin["x"] * ty_le), int(thong_tin["y"] * ty_le),
                int(thong_tin["r"] * ty_le), int(thong_tin["c"] * ty_le),
            )
        except RuntimeError:
            continue
        if thong_tin["pt"] > 0:
            chu = QFont(widget.font())
            chu.setPointSizeF(thong_tin["pt"] * ty_le)
            widget.setFont(chu)

def dat_vi_tri_co_gian(cua_so, widget, x, y, r, c):
    if not hasattr(cua_so, "_danh_sach_widget_co_gian"):
        widget.setGeometry(x, y, r, c)
        return
    cua_so._danh_sach_widget_co_gian = [
        thong_tin for thong_tin in cua_so._danh_sach_widget_co_gian if thong_tin["widget"] is not widget
    ]
    chu = widget.font()
    diem = chu.pointSizeF() if chu.pointSizeF() > 0 else float(chu.pointSize())
    cua_so._danh_sach_widget_co_gian.append({
        "widget": widget, "x": x, "y": y, "r": r, "c": c, "pt": max(diem, 0.0),
    })
    chieu_rong_goc, chieu_cao_goc = cua_so._kich_thuoc_goc
    if chieu_rong_goc <= 0 or chieu_cao_goc <= 0:
        widget.setGeometry(x, y, r, c)
        return
    ty_le = min(cua_so.width() / chieu_rong_goc, cua_so.height() / chieu_cao_goc)
    widget.setGeometry(int(x * ty_le), int(y * ty_le), int(r * ty_le), int(c * ty_le))
    if diem > 0:
        moi = QFont(widget.font())
        moi.setPointSizeF(diem * ty_le)
        widget.setFont(moi)

def load_users_data():
    danh_sach_nguoi_dung = list()
    duong_dan = lay_duong_dan_giao_dien("users.json")
    if os.path.exists(duong_dan):
        with open(duong_dan, "r", encoding="utf-8") as json_in:
            json_data = json.load(json_in)
            danh_sach_nguoi_dung.extend(json_data)
    return danh_sach_nguoi_dung

def write_users_data(json_data):
    duong_dan = lay_duong_dan_giao_dien("users.json")
    with open(duong_dan, "w", encoding="utf-8") as json_out:
        json.dump(json_data, json_out, ensure_ascii=False, indent=2)

class CuaSoDangNhap(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(lay_duong_dan_giao_dien("spck-login.ui"), self)
        self.pushButton_2.clicked.connect(self.dang_nhap)
        self.pushButton_4.clicked.connect(self.mo_dang_ky)
        self.lineEdit_2.setEchoMode(self.lineEdit_2.EchoMode.Password)
        self.hien_mat_khau = False
        if hasattr(self, "label_6"):
            self.label_6.mousePressEvent = lambda su_kien: self.thay_doi_hien_mat_khau()
        gan_co_gian(self, 410, 300)

    def dang_nhap(self):
        email = self.lineEdit.text().strip()
        mat_khau = self.lineEdit_2.text().strip()
        if not email or not mat_khau:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập email và mật khẩu")
            return
        danh_sach_nguoi_dung = load_users_data()
        for nguoi_dung in danh_sach_nguoi_dung:
            if nguoi_dung.get("email") == email:
                if nguoi_dung.get("mat_khau") == mat_khau:
                    ten_dang_nhap = nguoi_dung.get("ten_dang_nhap")
                    so_tien = load_so_tien_data(ten_dang_nhap)["so_tien_hien_tai"]
                    self.mo_cua_so_chinh(ten_dang_nhap, so_tien)
                    return
                QMessageBox.warning(self, "Lỗi", "Mật khẩu không đúng")
                return
        QMessageBox.warning(self, "Lỗi", "Tài khoản không tồn tại")

    def mo_dang_ky(self):
        self.cua_so_dang_ky = CuaSoDangKy(p=self)
        self.cua_so_dang_ky.show()
        self.hide()

    def mo_hoi_tien(self, ten_dang_nhap):
        self.cua_so_hoi_tien = CuaSoHoiTien(ten_dang_nhap)
        self.cua_so_hoi_tien.show()
        self.close()

    def mo_cua_so_chinh(self, ten_dang_nhap, so_tien):
        self.cua_so_chinh = CuaSoChinh(ten_dang_nhap, so_tien)
        self.cua_so_chinh.show()
        self.close()

    def thay_doi_hien_mat_khau(self):
        self.hien_mat_khau = not self.hien_mat_khau
        if self.hien_mat_khau:
            self.lineEdit_2.setEchoMode(self.lineEdit_2.EchoMode.Normal)
        else:
            self.lineEdit_2.setEchoMode(self.lineEdit_2.EchoMode.Password)


class CuaSoDangKy(QDialog):
    def __init__(self, p=None):
        super().__init__()
        uic.loadUi(lay_duong_dan_giao_dien("spck-signup.ui"), self)
        self.cua_so_cha = p
        self.pushButton_3.clicked.connect(self.dang_ky)
        if hasattr(self, "label_7"):
            self.label_7.mousePressEvent = lambda su_kien: self.quay_lai()
        if hasattr(self, "lineEdit_5"):
            self.lineEdit_5.setEchoMode(self.lineEdit_5.EchoMode.Password)
        self.dang_hien_mat_khau = False
        if hasattr(self, "label_8"):
            self.label_8.mousePressEvent = lambda su_kien: self.thay_doi_hien_mat_khau()
        gan_co_gian(self, 413, 300)

    def dang_ky(self):
        email = self.lineEdit_3.text().strip() if hasattr(self, "lineEdit_3") else ""
        ten_dang_nhap = self.lineEdit_4.text().strip() if hasattr(self, "lineEdit_4") else ""
        mat_khau = self.lineEdit_5.text() if hasattr(self, "lineEdit_5") else ""
        dong_y_dieu_khoan = self.checkBox.isChecked() if hasattr(self, "checkBox") else True

        trung_lap = False
        danh_sach_nguoi_dung = load_users_data()
        for nguoi_dung in danh_sach_nguoi_dung:
            if nguoi_dung.get("ten_dang_nhap") == ten_dang_nhap or nguoi_dung.get("email") == email:
                trung_lap = True
                break

        if len(mat_khau) < 8 or " " in mat_khau:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu phải từ 8 ký tự và không có dấu cách")
            return
        if "@" not in email or ".com" not in email:
            QMessageBox.warning(self, "Lỗi", "Email không hợp lệ")
            return
        if trung_lap:
            QMessageBox.warning(self, "Lỗi", "Tên đăng nhập hoặc email đã tồn tại")
            return
        if not dong_y_dieu_khoan:
            QMessageBox.warning(self, "Lỗi", "Vui lòng đồng ý điều khoản")
            return

        danh_sach_nguoi_dung.append({
            "ten_dang_nhap": ten_dang_nhap,
            "mat_khau": mat_khau,
            "email": email
        })
        write_users_data(danh_sach_nguoi_dung)

        QMessageBox.information(self, "Thành công", "Đăng ký thành công")
        if self.cua_so_cha:
            self.cua_so_cha.close()
        self.mo_hoi_tien(ten_dang_nhap)

    def mo_hoi_tien(self, ten_dang_nhap):
        self.cua_so_hoi_tien = CuaSoHoiTien(ten_dang_nhap)
        self.cua_so_hoi_tien.show()
        self.close()

    def quay_lai(self):
        if self.cua_so_cha:
            self.cua_so_cha.show()
        self.close()

    def thay_doi_hien_mat_khau(self):
        self.dang_hien_mat_khau = not self.dang_hien_mat_khau
        if hasattr(self, "lineEdit_5"):
            if self.dang_hien_mat_khau:
                self.lineEdit_5.setEchoMode(self.lineEdit_5.EchoMode.Normal)
            else:
                self.lineEdit_5.setEchoMode(self.lineEdit_5.EchoMode.Password)

def load_so_tien_data(ten_dang_nhap):
    so_tien_data = {"so_tien_hien_tai": 0.0, "so_tien_ban_dau": 0.0}
    duong_dan = lay_duong_dan_nguoi_dung(ten_dang_nhap, "sotien.json")
    if os.path.exists(duong_dan):
        with open(duong_dan, "r", encoding="utf-8") as json_in:
            so_tien_data = json.load(json_in)
    return so_tien_data

def write_so_tien_data(ten_dang_nhap, json_data):
    duong_dan = lay_duong_dan_nguoi_dung(ten_dang_nhap, "sotien.json")
    with open(duong_dan, "w", encoding="utf-8") as json_out:
        json.dump(json_data, json_out, ensure_ascii=False, indent=2)

class CuaSoHoiTien(QDialog):
    def __init__(self, ten_dang_nhap=""):
        super().__init__()
        uic.loadUi(lay_duong_dan_giao_dien("spck-ask.ui"), self)
        self.ten_dang_nhap = ten_dang_nhap
        self.pushButton_4.clicked.connect(self.kiem_tra_so_tien)
        gan_co_gian(self, 411, 300)

    def kiem_tra_so_tien(self):
        so_tien = self.lineEdit_6.text().strip() if hasattr(self, "lineEdit_6") else ""
        if not so_tien:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập số tiền")
            return
        try:
            so_tien_thuc = float(so_tien)
            if so_tien_thuc < 1000:
                raise ValueError
        except Exception:
            QMessageBox.warning(self, "Lỗi", "Số tiền không hợp lệ hoặc phải > 1000")
            return

        du_lieu_so_tien = load_so_tien_data(self.ten_dang_nhap)
        du_lieu_so_tien["so_tien_hien_tai"] = so_tien_thuc
        if du_lieu_so_tien["so_tien_ban_dau"] == 0.0:
            du_lieu_so_tien["so_tien_ban_dau"] = so_tien_thuc
        write_so_tien_data(self.ten_dang_nhap, du_lieu_so_tien)

        self.cua_so_chinh = CuaSoChinh(self.ten_dang_nhap, so_tien_thuc)
        self.cua_so_chinh.show()
        self.close()

def load_danh_muc_data(ten_dang_nhap):
    danh_sach_danh_muc = list()
    duong_dan = lay_duong_dan_nguoi_dung(ten_dang_nhap, "danhmuc.json")
    if os.path.exists(duong_dan):
        with open(duong_dan, "r", encoding="utf-8") as json_in:
            json_data = json.load(json_in)
            danh_sach_danh_muc.extend(json_data)
    return danh_sach_danh_muc

def write_danh_muc_data(ten_dang_nhap, json_data):
    duong_dan = lay_duong_dan_nguoi_dung(ten_dang_nhap, "danhmuc.json")
    with open(duong_dan, "w", encoding="utf-8") as json_out:
        json.dump(json_data, json_out, ensure_ascii=False, indent=2)

class CuaSoChinh(QDialog):
    def __init__(self, ten_dang_nhap="", so_du=0):
        super().__init__()
        uic.loadUi(lay_duong_dan_giao_dien("spck-main.ui"), self)
        self.ten_dang_nhap = ten_dang_nhap
        self.so_du = so_du
        self.danh_sach_danh_muc = []
        self.danh_sach_nhan_danh_muc = []
        self.cua_so_danh_muc = {}
        self.label_13.setText(f"<html><head/><body><p><span style=\" color:#ffffff;\">{ten_dang_nhap}</span></p></body></html>")
        self.label_12.setText(f"<html><head/><body><p><span style=\" color:#ffffff;\">{int(so_du)}</span></p></body></html>")
        dat_chu_dam(self, ["label_12", "label_13", "label_5"])
        if hasattr(self, "label_13"):
            font = self.label_13.font()
            font.setPointSize(28)
            self.label_13.setFont(font)
        if hasattr(self, "label_14"):
            self.label_14.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_14.mousePressEvent = lambda su_kien: self.mo_thong_ke()
        if hasattr(self, "label_7"):
            self.label_7.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_7.mousePressEvent = lambda su_kien: self.mo_thong_ke()
        if hasattr(self, "label_15"):
            self.label_15.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_15.mousePressEvent = lambda su_kien: self.mo_ghi_chu()
        if hasattr(self, "label_8"):
            self.label_8.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_8.mousePressEvent = lambda su_kien: self.mo_ghi_chu()
        if hasattr(self, "label_9"):
            self.label_9.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_9.mousePressEvent = lambda su_kien: self.mo_tim_kiem()
        if hasattr(self, "label_6"):
            self.label_6.setCursor(Qt.CursorShape.PointingHandCursor)
        if hasattr(self, "label_11"):
            self.label_11.setCursor(Qt.CursorShape.PointingHandCursor)
        if hasattr(self, "label_2"):
            chu = QFont()
            chu.setPointSize(24)
            chu.setBold(True)
            self.label_2.setFont(chu)
            self.label_2.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_2.mousePressEvent = lambda su_kien: self.mo_them_danh_muc()
            self.label_2.raise_()
        if hasattr(self, "pushButton"):
            self.pushButton.clicked.connect(self.mo_thong_ke)
        if hasattr(self, "label_10"):
            self.label_10.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_10.mousePressEvent = lambda su_kien: self.mo_cai_dat()
        self.tai_danh_sach_danh_muc()
        gan_co_gian(self, 421, 384)

    def mo_thong_ke(self):
        if not hasattr(self, "cua_so_thong_ke") or not self.cua_so_thong_ke:
            self.cua_so_thong_ke = CuaSoThongKe(p=self)
        self.cua_so_thong_ke.hien_thi_thong_ke()
        self.cua_so_thong_ke.show()
        self.hide()

    def mo_ghi_chu(self):
        if not hasattr(self, "cua_so_ghi_chu") or not self.cua_so_ghi_chu:
            self.cua_so_ghi_chu = CuaSoGhiChu(p=self)
        self.cua_so_ghi_chu.tai_ghi_chu()
        self.cua_so_ghi_chu.show()
        self.hide()

    def mo_tim_kiem(self):
        if not hasattr(self, "cua_so_tim_kiem") or not self.cua_so_tim_kiem:
            self.cua_so_tim_kiem = CuaSoTimKiem(p=self)
        self.cua_so_tim_kiem.show()
        self.hide()

    def mo_cai_dat(self):
        self.cua_so_cai_dat = CuaSoCaiDat(p=self)
        self.cua_so_cai_dat.show()

    def tai_danh_sach_danh_muc(self):
        danh_sach = load_danh_muc_data(self.ten_dang_nhap)
        for ten_danh_muc in danh_sach:
            self.them_danh_muc_vao_giao_dien(ten_danh_muc)

    def luu_danh_sach_danh_muc(self):
        write_danh_muc_data(self.ten_dang_nhap, self.danh_sach_danh_muc)

    def them_danh_muc_vao_giao_dien(self, ten_danh_muc):
        if ten_danh_muc in self.danh_sach_danh_muc:
            return
        self.danh_sach_danh_muc.append(ten_danh_muc)
        self.luu_danh_sach_danh_muc()
        nhan = QLabel(self)
        vi_tri = len(self.danh_sach_nhan_danh_muc)
        hang, cot = divmod(vi_tri, 4)
        dat_vi_tri_co_gian(self, nhan, 94 + cot * 70, 129 + hang * 80, 61, 71)
        nhan.setStyleSheet("background-color: #ffffff; border: 2px solid #2E8B57; border-radius: 12px; padding: 12px; font-weight: bold;")
        nhan.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nhan.setCursor(Qt.CursorShape.PointingHandCursor)
        nhan.setText(ten_danh_muc)
        nhan.mousePressEvent = lambda su_kien, muc=ten_danh_muc: self.xu_ly_nhan_danh_muc(su_kien, muc)
        nhan.show()
        if nhan not in self.danh_sach_nhan_danh_muc:
            self.danh_sach_nhan_danh_muc.append(nhan)

    def them_danh_muc(self, ten_danh_muc):
        self.them_danh_muc_vao_giao_dien(ten_danh_muc)

    def xu_ly_nhan_danh_muc(self, su_kien, ten_danh_muc):
        if su_kien.button() == Qt.MouseButton.LeftButton:
            self.mo_danh_muc(ten_danh_muc)
        elif su_kien.button() == Qt.MouseButton.RightButton:
            tra_loi = QMessageBox.question(
                self,
                "Xác nhận xóa",
                f"Bạn có muốn xóa mục '{ten_danh_muc}'?\nTất cả chi tiêu trong mục sẽ bị xóa.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if tra_loi == QMessageBox.StandardButton.Yes:
                self.xoa_danh_muc(ten_danh_muc)

    def xoa_danh_muc(self, ten_danh_muc):
        """Xóa danh mục và toàn bộ lịch sử chi tiêu của nó"""
        if ten_danh_muc not in self.danh_sach_danh_muc:  # Nếu danh mục không tồn tại, thoát
            return
        self.danh_sach_danh_muc.remove(ten_danh_muc)  # Xóa danh mục khỏi danh sách trong bộ nhớ
        write_danh_muc_data(self.ten_dang_nhap, self.danh_sach_danh_muc)  # Lưu lại danh sách danh mục
        du_lieu_chi_tieu = load_chi_tieu_data(self.ten_dang_nhap)  # Tải lịch sử chi tiêu
        if ten_danh_muc in du_lieu_chi_tieu:  # Nếu danh mục có lịch sử chi tiêu
            del du_lieu_chi_tieu[ten_danh_muc]  # Xóa toàn bộ lịch sử chi tiêu của danh mục đó
            write_chi_tieu_data(self.ten_dang_nhap, du_lieu_chi_tieu)  # Lưu thay đổi vào file chitieu.json
        for vi_tri, nhan in enumerate(self.danh_sach_nhan_danh_muc):  # Tìm và ẩn nhãn của danh mục đã xóa
            if nhan.text() == ten_danh_muc:
                nhan.hide()
                self.danh_sach_nhan_danh_muc.pop(vi_tri)
                break
        self.sap_xep_lai_danh_muc()  # Sắp xếp lại các nhãn danh mục

    def sap_xep_lai_danh_muc(self):
        for vi_tri, nhan in enumerate(self.danh_sach_nhan_danh_muc):
            hang, cot = divmod(vi_tri, 4)
            dat_vi_tri_co_gian(self, nhan, 94 + cot * 70, 129 + hang * 80, 61, 71)

    def mo_them_danh_muc(self):
        self.cua_so_them_danh_muc = CuaSoThemDanhMuc(p=self)
        self.cua_so_them_danh_muc.show()

    def mo_danh_muc(self, ten_danh_muc):
        if ten_danh_muc not in self.cua_so_danh_muc:
            self.cua_so_danh_muc[ten_danh_muc] = CuaSoDanhMuc(ten_danh_muc, p=self)
        self.cua_so_danh_muc[ten_danh_muc].show()

    def cap_nhat_so_du(self, dau, so_tien_str):
        try:
            gia_tri = float(so_tien_str)
            if dau == "+":
                self.so_du += gia_tri
            else:
                self.so_du -= gia_tri
        except Exception:
            return
        self.label_12.setText(f"<html><head/><body><p><span style=\" color:#ffffff;\">{int(self.so_du)}</span></p></body></html>")
        du_lieu_so_tien = load_so_tien_data(self.ten_dang_nhap)
        du_lieu_so_tien["so_tien_hien_tai"] = self.so_du
        write_so_tien_data(self.ten_dang_nhap, du_lieu_so_tien)

    def cap_nhat_tien(self, dau, so_tien_str):
        self.cap_nhat_so_du(dau, so_tien_str)

class CuaSoThongKe(QDialog):
    def __init__(self, p=None):
        super().__init__()
        uic.loadUi(lay_duong_dan_giao_dien("spck-thogke.ui"), self)
        self.cua_so_cha = p
        self.ten_dang_nhap = p.ten_dang_nhap if p else ""
        if hasattr(self, "label_15"):
            self.label_15.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_15.mousePressEvent = lambda su_kien: self.mo_cai_dat()

        if hasattr(self, "label_21"):
            self.label_21.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_21.mousePressEvent = lambda su_kien: self.mo_trang_chu()
        if hasattr(self, "label_28"):
            self.label_28.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_28.mousePressEvent = lambda su_kien: self.mo_ghi_chu()
        if hasattr(self, "label_19"):
            self.label_19.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_19.mousePressEvent = lambda su_kien: self.mo_tim_kiem()

        gan_co_gian(self, 418, 397)

    def mo_trang_chu(self):
        if self.cua_so_cha:
            self.cua_so_cha.show()
            self.hide()

    def mo_ghi_chu(self):
        if self.cua_so_cha:
            self.cua_so_cha.mo_ghi_chu()
            self.hide()

    def mo_tim_kiem(self):
        if self.cua_so_cha:
            self.cua_so_cha.mo_tim_kiem()
            self.hide()

    def mo_cai_dat(self):
        self.cua_so_cai_dat = CuaSoCaiDat(p=self.cua_so_cha)
        self.cua_so_cai_dat.show()

    def hien_thi_thong_ke(self):
        """Hiển thị thống kê tổng thu, tổng chi dựa trên lịch sử chi tiêu"""
        tong_thu = 0.0  # Tổng số tiền thu được
        tong_chi = 0.0  # Tổng số tiền chi ra

        du_lieu_chi_tieu = load_chi_tieu_data(self.ten_dang_nhap)  # Tải toàn bộ lịch sử chi tiêu từ chitieu.json
        for ten_danh_muc, chi_tieu in du_lieu_chi_tieu.items():  # Duyệt qua từng danh mục và lịch sử chi tiêu của nó
            for ct in chi_tieu:  # Duyệt qua từng chi tiêu trong danh mục
                try:
                    so_tien = ct["amount"]  # Lấy số tiền của chi tiêu (dạng "+/-xxxx")
                    gia_tri = float(so_tien[1:])  # Chuyển phần số sau dấu +/- sang số thực
                    if so_tien.startswith("+"):  # Nếu là tiền thu được
                        tong_thu += gia_tri  # Cộng vào tổng thu
                    else:  # Nếu là tiền chi ra
                        tong_chi += gia_tri  # Cộng vào tổng chi
                except Exception:  # Nếu có lỗi (ví dụ: số tiền không hợp lệ), bỏ qua chi tiêu này
                    continue

        du_lieu_so_tien = load_so_tien_data(self.ten_dang_nhap)  # Tải dữ liệu số tiền từ sotien.json
        so_tien_ban_dau = du_lieu_so_tien["so_tien_ban_dau"]
        so_tien_hien_tai = self.cua_so_cha.so_du if self.cua_so_cha else du_lieu_so_tien["so_tien_hien_tai"]

        chu_dam = QFont()
        chu_dam.setBold(True)

        if hasattr(self, "label_32"):
            self.label_32.setText(f"{int(so_tien_ban_dau):,} đ")
            self.label_32.setFont(chu_dam)
            self.label_32.setStyleSheet("color: #000000;")

        if hasattr(self, "label_35"):
            self.label_35.setText(f"{int(so_tien_hien_tai):,} đ")
            self.label_35.setFont(chu_dam)
            self.label_35.setStyleSheet("color: #000000;")

        if hasattr(self, "label_33"):
            self.label_33.setText(f"-{int(tong_chi):,} đ")
            self.label_33.setFont(chu_dam)
            self.label_33.setStyleSheet("color: #aa0000;")

        if hasattr(self, "label_34"):
            self.label_34.setText(f"+{int(tong_thu):,} đ")
            self.label_34.setFont(chu_dam)
            self.label_34.setStyleSheet("color: #00aa00;")

        if so_tien_hien_tai > 0:
            if hasattr(self, "label_28"):
                self.label_28.hide()
            if hasattr(self, "label_26"):
                self.label_26.setText("Hiện tại số")
                self.label_26.setFont(chu_dam)
                self.label_26.setStyleSheet("color: #00aa00;")
            if hasattr(self, "label_27"):
                self.label_27.setText("tiền đang dương")
                self.label_27.setFont(chu_dam)
                self.label_27.setStyleSheet("color: #00aa00;")
        else:
            if hasattr(self, "label_26"):
                self.label_26.setFont(chu_dam)
            if hasattr(self, "label_27"):
                self.label_27.setFont(chu_dam)
            if hasattr(self, "label_28"):
                self.label_28.setFont(chu_dam)

        if tong_thu > tong_chi:
            if hasattr(self, "label_29"):
                self.label_29.setText("Số tiền được thêm lớn")
                self.label_29.setFont(chu_dam)
                self.label_29.setStyleSheet("color: #00aa00;")
            if hasattr(self, "label_30"):
                self.label_30.setText("hơn số tiền đã tiêu")
                self.label_30.setFont(chu_dam)
                self.label_30.setStyleSheet("color: #00aa00;")
        else:
            if hasattr(self, "label_29"):
                self.label_29.setFont(chu_dam)
            if hasattr(self, "label_30"):
                self.label_30.setFont(chu_dam)
def load_ghi_chu_data(ten_dang_nhap):
    ghi_chu_data = {"ghi_chu": ""}
    duong_dan = lay_duong_dan_nguoi_dung(ten_dang_nhap, "ghichu.json")
    if os.path.exists(duong_dan):
        with open(duong_dan, "r", encoding="utf-8") as json_in:
            ghi_chu_data = json.load(json_in)
    return ghi_chu_data.get("ghi_chu", "")

def write_ghi_chu_data(ten_dang_nhap, noi_dung):
    duong_dan = lay_duong_dan_nguoi_dung(ten_dang_nhap, "ghichu.json")
    with open(duong_dan, "w", encoding="utf-8") as json_out:
        json.dump({"ghi_chu": noi_dung}, json_out, ensure_ascii=False, indent=2)

class CuaSoGhiChu(QDialog):
    def __init__(self, p=None):
        super().__init__()
        uic.loadUi(lay_duong_dan_giao_dien("spck-ghichu.ui"), self)
        self.cua_so_cha = p
        self.ten_dang_nhap = p.ten_dang_nhap if p else ""

        if hasattr(self, "label_25"):
            self.label_25.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_25.mousePressEvent = lambda su_kien: self.mo_trang_chu()

        if hasattr(self, "label_21"):
            self.label_21.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_21.mousePressEvent = lambda su_kien: self.mo_thong_ke()

        if hasattr(self, "label_24"):
            self.label_24.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_24.mousePressEvent = lambda su_kien: self.mo_tim_kiem()

        gan_co_gian(self, 418, 397)

    def tai_ghi_chu(self):
        try:
            noi_dung = load_ghi_chu_data(self.ten_dang_nhap)
            if hasattr(self, "textEdit"):
                self.textEdit.setText(noi_dung)
        except Exception as e:
            print(f"Lỗi khi tải ghi chú: {e}")

    def luu_ghi_chu(self):
        try:
            if hasattr(self, "textEdit"):
                write_ghi_chu_data(self.ten_dang_nhap, self.textEdit.toPlainText())
        except Exception as e:
            print(f"Lỗi khi lưu ghi chú: {e}")

    def closeEvent(self, event):
        self.luu_ghi_chu()
        super().closeEvent(event)

    def mo_trang_chu(self):
        self.luu_ghi_chu()
        if self.cua_so_cha:
            self.cua_so_cha.show()
            self.hide()

    def mo_thong_ke(self):
        self.luu_ghi_chu()
        if self.cua_so_cha:
            self.cua_so_cha.mo_thong_ke()
            self.hide()

    def mo_tim_kiem(self):
        self.luu_ghi_chu()
        if self.cua_so_cha:
            self.cua_so_cha.mo_tim_kiem()
            self.hide()

def xoa_dau_tieng_viet(s):
    s = s.lower()
    mapping = {
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'đ': 'd',
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y'
    }
    for k, v in mapping.items():
        s = s.replace(k, v)
    return s

class CuaSoTimKiem(QDialog):
    def __init__(self, p=None):
        super().__init__()
        uic.loadUi(lay_duong_dan_giao_dien("spck-tkiem.ui"), self)
        self.cua_so_cha = p
        self.ten_dang_nhap = p.ten_dang_nhap if p else ""
        self.danh_sach_nhan_goi_y = []

        if hasattr(self, "label_12"):
            self.label_12.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_12.mousePressEvent = lambda su_kien: self.mo_trang_chu()

        if hasattr(self, "label_14"):
            self.label_14.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_14.mousePressEvent = lambda su_kien: self.mo_thong_ke()

        if hasattr(self, "label_16"):
            self.label_16.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_16.mousePressEvent = lambda su_kien: self.mo_ghi_chu()

        if hasattr(self, "label_11"):
            self.label_11.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_11.mousePressEvent = lambda su_kien: self.goi_y_chi_tieu()

        # Thay thế QTextEdit bằng QLineEdit để tránh lỗi bộ gõ tiếng Việt và lỗi phím Enter xuống dòng
        if hasattr(self, "textEdit"):
            from PyQt6.QtWidgets import QLineEdit
            cha = self.textEdit.parent()
            toa_do = self.textEdit.geometry()
            phong_cach = self.textEdit.styleSheet()

            self.o_tim_kiem = QLineEdit(cha if cha else self)
            self.o_tim_kiem.setGeometry(toa_do)
            self.o_tim_kiem.setStyleSheet(phong_cach)
            self.o_tim_kiem.setPlaceholderText("Tìm kiếm danh mục...")

            dat_vi_tri_co_gian(self, self.o_tim_kiem, toa_do.x(), toa_do.y(), toa_do.width(), toa_do.height())

            self.textEdit.hide()
            self.textEdit.deleteLater()

            self.textEdit = self.o_tim_kiem
            self.textEdit.textChanged.connect(self.goi_y_chi_tieu)

        # self.frame đã là QFrame sẵn trong file UI nên không cần thay thế tại runtime nữa
        if not hasattr(self, "frame"):
            self.frame = self

        gan_co_gian(self, 401, 300)

    def mo_trang_chu(self):
        if self.cua_so_cha:
            self.cua_so_cha.show()
            self.hide()

    def mo_thong_ke(self):
        if self.cua_so_cha:
            self.cua_so_cha.mo_thong_ke()
            self.hide()

    def mo_ghi_chu(self):
        if self.cua_so_cha:
            self.cua_so_cha.mo_ghi_chu()
            self.hide()

    def mo_danh_muc_chi_tiet(self, ten_danh_muc):
        if self.cua_so_cha:
            self.cua_so_cha.show()
            self.cua_so_cha.mo_danh_muc(ten_danh_muc)
            self.hide()

    def goi_y_chi_tieu(self, text_nhap=None):
        if not hasattr(self, "textEdit") or not hasattr(self, "frame"):
            return

        if not isinstance(text_nhap, str):
            text_nhap = self.textEdit.text()
        
        # Không dùng strip() ở đây để tránh triệt tiêu dấu cách trong khi người dùng đang gõ
        text_nhap_chuan = text_nhap.strip()

        for nhan in self.danh_sach_nhan_goi_y:
            try:
                if hasattr(self, "_danh_sach_widget_co_gian"):
                    self._danh_sach_widget_co_gian = [
                        thong_tin for thong_tin in self._danh_sach_widget_co_gian if thong_tin["widget"] is not nhan
                    ]
                nhan.hide()
                nhan.deleteLater()
            except RuntimeError:
                pass
        self.danh_sach_nhan_goi_y = []

        if not text_nhap_chuan:
            self.frame.repaint()
            return

        truy_van_khong_dau = xoa_dau_tieng_viet(text_nhap_chuan)
        danh_sach_khop = []

        if self.cua_so_cha and hasattr(self.cua_so_cha, "danh_sach_danh_muc"):
            for muc in self.cua_so_cha.danh_sach_danh_muc:
                muc_khong_dau = xoa_dau_tieng_viet(muc)
                if truy_van_khong_dau in muc_khong_dau:
                    chi_so = muc_khong_dau.find(truy_van_khong_dau)
                    danh_sach_khop.append((chi_so, muc))

        # Sắp xếp các danh mục khớp theo chỉ số xuất hiện tăng dần (càng gần đầu dòng càng được ưu tiên)
        danh_sach_khop.sort(key=lambda x: x[0])
        ket_qua_goi_y = [item[1] for item in danh_sach_khop]

        for vi_tri, ten_danh_muc in enumerate(ket_qua_goi_y):
            nhan = QLabel(self.frame)
            hang, cot = divmod(vi_tri, 4)
            dat_vi_tri_co_gian(self, nhan, 10 + cot * 70, 35 + hang * 80, 61, 71)
            nhan.setStyleSheet("background-color: #ffffff; border: 2px solid #2E8B57; border-radius: 12px; padding: 12px; font-weight: bold;")
            nhan.setAlignment(Qt.AlignmentFlag.AlignCenter)
            nhan.setCursor(Qt.CursorShape.PointingHandCursor)
            nhan.setText(ten_danh_muc)
            nhan.mousePressEvent = lambda su_kien, muc=ten_danh_muc: self.mo_danh_muc_chi_tiet(muc)
            nhan.show()
            self.danh_sach_nhan_goi_y.append(nhan)

        # Sử dụng repaint() thay vì update() để bắt buộc vẽ lại ngay lập tức
        for nhan in self.danh_sach_nhan_goi_y:
            nhan.repaint()
        self.frame.repaint()

class CuaSoCaiDat(QDialog):
    def __init__(self, p=None):
        super().__init__()
        uic.loadUi(lay_duong_dan_giao_dien("spck-settings.ui"), self)
        self.cua_so_cha = p
        self.ten_dang_nhap = p.ten_dang_nhap if p else ""
        if hasattr(self, "pushButton_2"):
            self.pushButton_2.clicked.connect(self.dang_xuat)
        if hasattr(self, "pushButton"):
            self.pushButton.clicked.connect(self.xoa_tai_khoan)
        gan_co_gian(self, 261, 142)

    def dang_xuat(self):
        tra_loi = QMessageBox.question(
            self,
            "Xác nhận đăng xuất",
            "Bạn có chắc muốn đăng xuất không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if tra_loi == QMessageBox.StandardButton.Yes:
            self.cua_so_dang_nhap = CuaSoDangNhap()
            self.cua_so_dang_nhap.show()
            if self.cua_so_cha:
                self.cua_so_cha.close()
            self.close()

    def xoa_tai_khoan(self):
        tra_loi = QMessageBox.question(
            self,
            "Xác nhận xóa tài khoản",
            "Bạn có chắc muốn xóa tài khoản?\nToàn bộ dữ liệu sẽ bị xóa vĩnh viễn!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if tra_loi != QMessageBox.StandardButton.Yes:
            return

        danh_sach_nguoi_dung = load_users_data()
        danh_sach_nguoi_dung = [nd for nd in danh_sach_nguoi_dung if nd.get("ten_dang_nhap") != self.ten_dang_nhap]
        write_users_data(danh_sach_nguoi_dung)

        thu_muc_tai_khoan = os.path.join(THU_MUC_CSDL, self.ten_dang_nhap)
        if os.path.exists(thu_muc_tai_khoan):
            shutil.rmtree(thu_muc_tai_khoan)

        QMessageBox.information(self, "Thành công", "Tài khoản đã được xóa")
        self.cua_so_dang_nhap = CuaSoDangNhap()
        self.cua_so_dang_nhap.show()
        if self.cua_so_cha:
            self.cua_so_cha.close()
        self.close()

class CuaSoThemDanhMuc(QDialog):
    def __init__(self, p=None):
        super().__init__()
        uic.loadUi(lay_duong_dan_giao_dien("spck-ttct.ui"), self)
        self.cua_so_cha = p
        self.lineEdit.setPlaceholderText("Nhập tên mục")
        self.pushButton_4.clicked.connect(self.xac_nhan_danh_muc)
        dat_chu_dam(self, ["label_8", "label_9", "label_10", "label_11"])
        gan_co_gian(self, 251, 171)

    def xac_nhan_danh_muc(self):
        ten_danh_muc = self.lineEdit.text().strip()
        if not ten_danh_muc:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên mục")
            return
        if self.cua_so_cha:
            self.cua_so_cha.them_danh_muc(ten_danh_muc)
        self.close()

def load_chi_tieu_data(ten_dang_nhap):
    chi_tieu_data = dict()
    duong_dan = lay_duong_dan_nguoi_dung(ten_dang_nhap, "chitieu.json")
    if os.path.exists(duong_dan):
        with open(duong_dan, "r", encoding="utf-8") as json_in:
            chi_tieu_data = json.load(json_in)
    return chi_tieu_data

def write_chi_tieu_data(ten_dang_nhap, json_data):
    duong_dan = lay_duong_dan_nguoi_dung(ten_dang_nhap, "chitieu.json")
    with open(duong_dan, "w", encoding="utf-8") as json_out:
        json.dump(json_data, json_out, ensure_ascii=False, indent=2)

class CuaSoDanhMuc(QDialog):
    def __init__(self, ten_danh_muc="", p=None):
        super().__init__()
        uic.loadUi(lay_duong_dan_giao_dien("spck-muc.ui"), self)
        self.ten_danh_muc = ten_danh_muc
        self.cua_so_cha = p
        self.ten_dang_nhap = p.ten_dang_nhap if p else ""
        self.label_16.setText(ten_danh_muc)
        self.label_19.hide()
        self.label_20.hide()
        self.danh_sach_hang_chi_tieu = []
        self.danh_sach_chi_tieu = []
        self.vi_tri_y = 160
        self.label_17.mousePressEvent = lambda su_kien: self.mo_cua_so_nhap_chi_tieu_moi()
        self.tai_chi_tieu()
        dat_chu_dam(self, ["label_16", "label_17"])
        gan_co_gian(self, 414, 415)

    def mo_cua_so_nhap_chi_tieu_moi(self):
        self.cua_so_nhap_moi = CuaSoNhapChiTieuMoi(p=self)
        self.cua_so_nhap_moi.show()

    def tao_hang_chi_tieu(self):
        nhan_ten = QLabel(self)
        dat_vi_tri_co_gian(self, nhan_ten, 20, self.vi_tri_y, 261, 31)
        nhan_ten.setStyleSheet("background-color: transparent;")
        nhan_ten.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        font_ten = QFont("Microsoft Tai Le", 14)
        font_ten.setBold(True)
        nhan_ten.setFont(font_ten)

        nhan_chi_tiet = QLabel(self)
        dat_vi_tri_co_gian(self, nhan_chi_tiet, 20, self.vi_tri_y + 20, 261, 31)
        nhan_chi_tiet.setStyleSheet("background-color: transparent;")
        nhan_chi_tiet.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        font_chi_tiet = QFont("Microsoft Tai Le", 12)
        font_chi_tiet.setBold(True)
        nhan_chi_tiet.setFont(font_chi_tiet)

        return nhan_ten, nhan_chi_tiet

    def hien_thi_chi_tieu(self, ten_chi_tieu, so_tien, ngay_thang, luu=True):
        """Hiển thị chi tiêu lên giao diện và lưu vào lịch sử nếu cần"""
        if not self.danh_sach_hang_chi_tieu:  # Nếu chưa có hàng chi tiêu nào, dùng các label có sẵn (label19 và label20)
            nhan_ten, nhan_chi_tiet = self.label_19, self.label_20
        else:  # Nếu đã có hàng chi tiêu, tạo các label mới
            nhan_ten, nhan_chi_tiet = self.tao_hang_chi_tieu()
        nhan_ten.setText(ten_chi_tieu)  # Đặt tên chi tiêu lên nhãn
        nhan_chi_tiet.setText(  # Đặt số tiền (màu xanh nếu là thu, đỏ nếu là chi) và ngày lên nhãn
            f"<html><head/><body><p><span style=\" color:{'#009900' if so_tien.startswith('+') else '#cc0000'};\">{so_tien}</span> <span style=\" color:#000000;\">{ngay_thang}</span></p></body></html>"
        )
        nhan_ten.show()  # Hiển thị nhãn tên chi tiêu
        nhan_chi_tiet.show()  # Hiển thị nhãn chi tiết
        self.danh_sach_hang_chi_tieu.append((nhan_ten, nhan_chi_tiet))  # Thêm cặp nhãn vào danh sách hàng chi tiêu
        if luu:  # Nếu cần lưu (thêm chi tiêu mới), thêm vào danh sách và lưu vào file JSON
            self.danh_sach_chi_tieu.append((ten_chi_tieu, so_tien, ngay_thang))  # Thêm chi tiêu vào danh sách trong bộ nhớ
            self.luu_chi_tieu()  # Lưu lịch sử chi tiêu vào file chitieu.json
        if luu and self.cua_so_cha:  # Chỉ cập nhật số tiền hiện tại khi đây là giao dịch mới (luu=True)
            self.cua_so_cha.cap_nhat_tien(so_tien[0], so_tien[1:])  # Cập nhật số tiền (dấu +/-, phần số)
        self.vi_tri_y += 60  # Tăng vị trí y để hàng chi tiêu tiếp theo ở dưới

    def tai_chi_tieu(self):
        """Tải lịch sử chi tiêu của danh mục hiện tại từ chitieu.json"""
        du_lieu_chi_tieu = load_chi_tieu_data(self.ten_dang_nhap)  # Tải toàn bộ lịch sử chi tiêu của người dùng
        if self.ten_danh_muc in du_lieu_chi_tieu:  # Kiểm tra xem danh mục có lịch sử chi tiêu không
            for chi_tieu in du_lieu_chi_tieu[self.ten_danh_muc]:  # Duyệt qua từng chi tiêu trong lịch sử
                self.hien_thi_chi_tieu(chi_tieu["name"], chi_tieu["amount"], chi_tieu["date"], luu=False)  # Hiển thị chi tiêu lên giao diện (không lưu lại)
                self.danh_sach_chi_tieu.append((chi_tieu["name"], chi_tieu["amount"], chi_tieu["date"]))  # Thêm chi tiêu vào danh sách trong bộ nhớ

    def luu_chi_tieu(self):
        """Lưu lịch sử chi tiêu của danh mục hiện tại vào chitieu.json"""
        du_lieu_chi_tieu = load_chi_tieu_data(self.ten_dang_nhap)  # Tải dữ liệu chi tiêu hiện tại của người dùng
        du_lieu_chi_tieu[self.ten_danh_muc] = [  # Cập nhật lịch sử chi tiêu cho danh mục hiện tại
            {"name": ten, "amount": tien, "date": ngay}  # Chuyển mỗi chi tiêu từ tuple sang dictionary để lưu vào JSON
            for ten, tien, ngay in self.danh_sach_chi_tieu  # Duyệt qua danh sách chi tiêu trong bộ nhớ
        ]
        write_chi_tieu_data(self.ten_dang_nhap, du_lieu_chi_tieu)  # Lưu toàn bộ lịch sử chi tiêu vào chitieu.json

    def hien_thi_chi_tieu_goi(self, ten_chi_tieu, so_tien, ngay_thang, luu=True):
        self.hien_thi_chi_tieu(ten_chi_tieu, so_tien, ngay_thang, luu=luu)

class CuaSoNhapChiTieuMoi(QDialog):
    def __init__(self, p=None):
        super().__init__()
        uic.loadUi(lay_duong_dan_giao_dien("spck-nl.ui"), self)
        self.cua_so_cha = p
        self.lineEdit.setPlaceholderText("Nhập ngày")
        self.lineEdit_2.setPlaceholderText("Nhập số tiền(+/-)")
        self.lineEdit_3.setPlaceholderText("Tên chi tiêu")
        self.pushButton_3.clicked.connect(self.gui_chi_tieu)
        dat_chu_dam(self, ["label_13", "label_14", "label_21"])
        if hasattr(self, "label_13"):
            font = self.label_13.font()
            font.setPointSize(28)
            self.label_13.setFont(font)
        gan_co_gian(self, 400, 300)

    def phan_tich_ngay(self, ngay):
        phan = [pt.strip() for pt in ngay.split("/")]
        if len(phan) != 3:
            return None
        try:
            return datetime(int(phan[2]), int(phan[1]), int(phan[0])).strftime("%d/%m/%Y")
        except Exception:
            return None

    def gui_chi_tieu(self):
        ngay = self.lineEdit.text().strip()
        so_tien = self.lineEdit_2.text().strip()
        ten_chi_tieu = self.lineEdit_3.text().strip()
        if not all([ngay, so_tien, ten_chi_tieu]):
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đủ thông tin")
            return
        if so_tien[0] not in "+-":
            QMessageBox.warning(self, "Lỗi", "Số tiền phải bắt đầu bằng + hoặc -")
            return
        if not so_tien[1:].replace('.', '', 1).isdigit():
            QMessageBox.warning(self, "Lỗi", "Số tiền không hợp lệ")
            return
        ngay_hop_le = self.phan_tich_ngay(ngay)
        if not ngay_hop_le:
            QMessageBox.warning(self, "Lỗi", "Ngày không hợp lệ")
            return
        if self.cua_so_cha:
            self.cua_so_cha.hien_thi_chi_tieu(ten_chi_tieu, so_tien, ngay_hop_le)
        self.close()

if __name__ == "__main__":
    ung_dung = QApplication(sys.argv)
    CuaSoDangNhap().show()
    sys.exit(ung_dung.exec())