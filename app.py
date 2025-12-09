from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'rahasia123'

# Database SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "lintang_chicken.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model Sederhana
class Barang(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kode = db.Column(db.String(20), unique=True)
    nama = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.String(50))
    stok = db.Column(db.Integer, default=0)
    harga = db.Column(db.Integer, default=0)
    satuan = db.Column(db.String(20), default='pcs')

# Buat database
with app.app_context():
    db.create_all()
    
    # Tambah 3 barang contoh jika kosong
    if Barang.query.count() == 0:
        barang_contoh = [
            Barang(kode='AYM001', nama='Dada Ayam Fillet', kategori='Ayam Potong', stok=50, harga=45000, satuan='kg'),
            Barang(kode='AYM002', nama='Paha Ayam Utuh', kategori='Ayam Potong', stok=35, harga=38000, satuan='kg'),
            Barang(kode='AYM003', nama='Sayap Ayam', kategori='Ayam Potong', stok=40, harga=35000, satuan='kg')
        ]
        db.session.add_all(barang_contoh)
        db.session.commit()

# Routes
@app.route('/')
def home():
    if 'logged_in' in session:
        return redirect('/dashboard')
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Login sederhana - hanya cek admin/admin123
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            session['username'] = 'admin'
            flash('Login berhasil!', 'success')
            return redirect('/dashboard')
        else:
            flash('Username/password salah!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout', 'success')
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect('/login')
    
    total_barang = Barang.query.count()
    total_stok = db.session.query(db.func.sum(Barang.stok)).scalar() or 0
    
    return render_template('index.html', 
                         total_barang=total_barang,
                         total_stok=total_stok)

@app.route('/barang')
def daftar_barang():
    if 'logged_in' not in session:
        return redirect('/login')
    
    items = Barang.query.order_by(Barang.nama).all()
    return render_template('daftar_barang.html', items=items)

@app.route('/barang/tambah', methods=['GET', 'POST'])
def tambah_barang():
    if 'logged_in' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        try:
            # Ambil data dari form
            kode = request.form.get('kode')
            nama = request.form.get('nama')
            kategori = request.form.get('kategori')
            stok = int(request.form.get('stok', 0))
            harga = int(request.form.get('harga', 0))
            satuan = request.form.get('satuan', 'pcs')
            
            # Cek duplikat kode
            existing = Barang.query.filter_by(kode=kode).first()
            if existing:
                flash('Kode barang sudah ada', 'error')
                return redirect('/barang/tambah')
            
            # Simpan ke database
            barang = Barang(
                kode=kode,
                nama=nama,
                kategori=kategori,
                stok=stok,
                harga=harga,
                satuan=satuan
            )
            
            db.session.add(barang)
            db.session.commit()
            
            flash('Barang berhasil ditambahkan!', 'success')
            return redirect('/barang')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('tambah_barang.html')

@app.route('/barang/<int:id>/edit', methods=['GET', 'POST'])
def edit_barang(id):
    if 'logged_in' not in session:
        return redirect('/login')
    
    barang = Barang.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            barang.nama = request.form.get('nama')
            barang.kategori = request.form.get('kategori')
            barang.stok = int(request.form.get('stok', 0))
            barang.harga = int(request.form.get('harga', 0))
            barang.satuan = request.form.get('satuan', 'pcs')
            
            db.session.commit()
            flash('Barang berhasil diupdate!', 'success')
            return redirect('/barang')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('edit_barang.html', item=barang)

@app.route('/barang/<int:id>/hapus')
def hapus_barang(id):
    if 'logged_in' not in session:
        return redirect('/login')
    
    try:
        barang = Barang.query.get_or_404(id)
        db.session.delete(barang)
        db.session.commit()
        flash('Barang berhasil dihapus', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect('/barang')

if __name__ == '__main__':
    app.run(debug=True, port=5000)