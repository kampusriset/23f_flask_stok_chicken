from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'lintang_chicken_secret_key_2024'  # Ganti dengan secret key yang kuat

# Data sementara (dalam aplikasi real, gunakan database)
items = [
    {"id": 1, "name": "Dada Ayam", "stock": 50, "category": "Ayam Potong", "price": 45000},
    {"id": 2, "name": "Paha Ayam", "stock": 35, "category": "Ayam Potong", "price": 38000},
    {"id": 3, "name": "Sayap Ayam", "stock": 40, "category": "Ayam Potong", "price": 35000}
]

# Data user (dalam aplikasi real, gunakan database dengan password terenkripsi)
users = {
    'admin': {
        'password': 'admin123',
        'name': 'Administrator',
        'role': 'admin'
    },
    'manager': {
        'password': 'manager123',
        'name': 'Manager Lintang',
        'role': 'manager'
    }
}

# Decorator untuk memeriksa login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Silakan login terlebih dahulu', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def dashboard():
    return render_template('index.html', items=items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Jika sudah login, redirect ke dashboard
    if 'user' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Cek kredensial
        if username in users and users[username]['password'] == password:
            session['user'] = {
                'username': username,
                'name': users[username]['name'],
                'role': users[username]['role']
            }
            flash(f'Selamat datang, {users[username]["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Anda telah berhasil logout', 'success')
    return redirect(url_for('login'))

@app.route('/tambah-barang', methods=['GET', 'POST'])
@login_required
def tambah_barang():
    if request.method == 'POST':
        name = request.form['name']
        stock = int(request.form['stock'])
        category = request.form['category']
        price = int(request.form['price'])
        new_id = max([item['id'] for item in items]) + 1 if items else 1
        items.append({"id": new_id, "name": name, "stock": stock, "category": category, "price": price})
        flash('Barang berhasil ditambahkan!', 'success')
        return redirect(url_for('daftar_barang'))
    return render_template('tambah_barang.html')

@app.route('/daftar-barang')
@login_required
def daftar_barang():
    return render_template('daftar_barang.html', items=items)

@app.route('/edit-barang/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_barang(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if not item:
        flash('Barang tidak ditemukan', 'error')
        return redirect(url_for('daftar_barang'))
    
    if request.method == 'POST':
        item['name'] = request.form['name']
        item['stock'] = int(request.form['stock'])
        item['category'] = request.form['category']
        item['price'] = int(request.form['price'])
        flash('Barang berhasil diupdate!', 'success')
        return redirect(url_for('daftar_barang'))
    
    return render_template('edit_barang.html', item=item)

@app.route('/hapus-barang/<int:item_id>')
@login_required
def hapus_barang(item_id):
    global items
    items = [item for item in items if item['id'] != item_id]
    flash('Barang berhasil dihapus!', 'success')
    return redirect(url_for('daftar_barang'))

if __name__ == '__main__':
    app.run(debug=True)