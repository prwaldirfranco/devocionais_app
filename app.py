from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "chave_secreta_segura"

DB_NAME = "devocionais.db"

# --- Inicializar banco ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Tabela devocionais
    c.execute("""
    CREATE TABLE IF NOT EXISTS devocionais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        conteudo TEXT NOT NULL,
        tipo TEXT NOT NULL DEFAULT 'devocional'
    )
    """)

    # Tabela curtidas
    c.execute("""
    CREATE TABLE IF NOT EXISTS curtidas (
        devocional_id INTEGER PRIMARY KEY,
        likes INTEGER DEFAULT 0,
        FOREIGN KEY(devocional_id) REFERENCES devocionais(id)
    )
    """)

    conn.commit()
    conn.close()

init_db()

# --- Lista de versículos (em português) ---
VERSICULOS = [
    ("Porque Deus amou o mundo de tal maneira que deu o seu Filho unigênito, para que todo aquele que nele crê não pereça, mas tenha a vida eterna.", "João 3:16"),
    ("O Senhor é o meu pastor, nada me faltará.", "Salmos 23:1"),
    ("Posso todas as coisas naquele que me fortalece.", "Filipenses 4:13"),
    ("Lâmpada para os meus pés é tua palavra e luz para o meu caminho.", "Salmos 119:105"),
    ("Entrega o teu caminho ao Senhor; confia nele, e ele tudo fará.", "Salmos 37:5"),
    ("Buscai primeiro o Reino de Deus e a sua justiça, e todas estas coisas vos serão acrescentadas.", "Mateus 6:33"),
    ("Não temas, porque eu sou contigo; não te assombres, porque eu sou o teu Deus.", "Isaías 41:10"),
    ("Alegrai-vos sempre no Senhor; outra vez digo: alegrai-vos.", "Filipenses 4:4"),
    ("Bem-aventurados os que têm fome e sede de justiça, porque serão fartos.", "Mateus 5:6"),
    ("O Senhor é a minha luz e a minha salvação; a quem temerei?", "Salmos 27:1"),
    ("O Senhor é bom, uma fortaleza no dia da angústia; e conhece os que confiam nele.", "Naum 1:7"),
    ("Deus é o nosso refúgio e fortaleza, socorro bem presente na angústia.", "Salmos 46:1"),
    ("Clama a mim, e responder-te-ei, e anunciar-te-ei coisas grandes e firmes que não sabes.", "Jeremias 33:3"),
    ("Honra teu pai e tua mãe, para que se prolonguem os teus dias na terra que o Senhor teu Deus te dá.", "Êxodo 20:12"),
    ("Amarás o Senhor teu Deus de todo o teu coração, de toda a tua alma e de toda a tua mente.", "Mateus 22:37"),
    ("Amarás o teu próximo como a ti mesmo.", "Mateus 22:39"),
    ("Portanto, ide e fazei discípulos de todas as nações, batizando-os em nome do Pai, e do Filho, e do Espírito Santo.", "Mateus 28:19"),
    ("Alegrai-vos na esperança, sede pacientes na tribulação, perseverai na oração.", "Romanos 12:12"),
    ("Mas buscai primeiro o Reino de Deus e a sua justiça, e todas estas coisas vos serão acrescentadas.", "Mateus 6:33"),
    ("O Senhor é a minha rocha, a minha fortaleza e o meu libertador.", "Salmos 18:2"),
    ("Não vos conformeis com este mundo, mas transformai-vos pela renovação da vossa mente.", "Romanos 12:2"),
    ("Se confessarmos os nossos pecados, ele é fiel e justo para nos perdoar os pecados e nos purificar de toda injustiça.", "1 João 1:9"),
    ("Confia no Senhor de todo o teu coração, e não te estribes no teu próprio entendimento.", "Provérbios 3:5"),
    ("O Senhor é bom para todos, e as suas misericórdias são sobre todas as suas obras.", "Salmos 145:9"),
    ("Lançando sobre ele toda a vossa ansiedade, porque ele tem cuidado de vós.", "1 Pedro 5:7"),
    ("Sede fortes e corajosos; não temais, nem vos assusteis diante deles, porque o Senhor vosso Deus é quem vai convosco.", "Deuteronômio 31:6"),
    ("Eu sou o caminho, a verdade e a vida; ninguém vem ao Pai senão por mim.", "João 14:6"),
    ("Mas o fruto do Espírito é amor, alegria, paz, longanimidade, benignidade, bondade, fidelidade.", "Gálatas 5:22"),
    ("Vinde a mim, todos os que estais cansados e oprimidos, e eu vos aliviarei.", "Mateus 11:28"),
    ("Em tudo dai graças, porque esta é a vontade de Deus em Cristo Jesus para convosco.", "1 Tessalonicenses 5:18"),
    ("Porque sou eu que conheço os planos que tenho para vós, diz o Senhor, planos de paz e não de mal, para vos dar o fim que desejais.", "Jeremias 29:11")
]

# --- Função para escolher versículo do dia ---
def versiculo_do_dia():
    hoje = date.today()
    index = hoje.toordinal() % len(VERSICULOS)  # índice baseado na data
    return VERSICULOS[index]

# --- Rota API para AJAX ---
@app.route("/api/versiculo")
def api_versiculo():
    texto, referencia = versiculo_do_dia()
    return jsonify({'texto': texto, 'referencia': referencia})

# --- Página inicial com busca ---
@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if query:
        c.execute("SELECT id, titulo, tipo, conteudo FROM devocionais WHERE titulo LIKE ?", ('%'+query+'%',))
    else:
        c.execute("SELECT id, titulo, tipo, conteudo FROM devocionais")
    devocionais = c.fetchall()

    # Curtidas
    c.execute("SELECT devocional_id, likes FROM curtidas")
    curtidas_data = {row[0]: row[1] for row in c.fetchall()}
    conn.close()

    # Versículo inicial
    versiculo = versiculo_do_dia()
    return render_template("index.html", devocionais=devocionais, curtidas_data=curtidas_data,
                           query=query, versiculo_texto=versiculo[0], versiculo_ref=versiculo[1])

# --- Visualizar devocional completo ---
@app.route("/view/<int:devocional_id>")
def view(devocional_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT titulo, conteudo, tipo FROM devocionais WHERE id=?", (devocional_id,))
    devocional = c.fetchone()
    conn.close()
    return render_template("view.html", devocional=devocional)

# --- Curtir devocional ---
@app.route("/like/<int:devocional_id>", methods=["POST"])
def like(devocional_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT likes FROM curtidas WHERE devocional_id=?", (devocional_id,))
    curtida = c.fetchone()
    if curtida:
        c.execute("UPDATE curtidas SET likes = likes + 1 WHERE devocional_id=?", (devocional_id,))
    else:
        c.execute("INSERT INTO curtidas (devocional_id, likes) VALUES (?, 1)", (devocional_id,))
    conn.commit()
    c.execute("SELECT likes FROM curtidas WHERE devocional_id=?", (devocional_id,))
    likes = c.fetchone()[0]
    conn.close()
    return jsonify({'likes': likes})

# --- Login admin ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        if usuario == "admin" and senha == "123":
            session["admin"] = True
            return redirect(url_for("admin"))
        else:
            return "Credenciais inválidas!"
    return render_template("login.html")

# --- Logout admin ---
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("index"))

# --- Painel admin ---
@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, titulo, tipo FROM devocionais")
    devocionais = c.fetchall()
    conn.close()
    return render_template("admin.html", devocionais=devocionais)

# --- Adicionar devocional ---
@app.route("/admin/add", methods=["POST"])
def add_devocional():
    if "admin" not in session:
        return redirect(url_for("login"))
    titulo = request.form["titulo"]
    conteudo = request.form["conteudo"]
    tipo = request.form.get("tipo", "devocional")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO devocionais (titulo, conteudo, tipo) VALUES (?, ?, ?)", (titulo, conteudo, tipo))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

# --- Editar devocional ---
@app.route("/admin/edit/<int:id>", methods=["GET", "POST"])
def edit_devocional(id):
    if "admin" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if request.method == "POST":
        titulo = request.form["titulo"]
        conteudo = request.form["conteudo"]
        tipo = request.form.get("tipo", "devocional")
        c.execute("UPDATE devocionais SET titulo=?, conteudo=?, tipo=? WHERE id=?", (titulo, conteudo, tipo, id))
        conn.commit()
        conn.close()
        return redirect(url_for("admin"))
    c.execute("SELECT titulo, conteudo, tipo FROM devocionais WHERE id=?", (id,))
    devocional = c.fetchone()
    conn.close()
    return render_template("edit.html", devocional=devocional, id=id)

# --- Excluir devocional ---
@app.route("/admin/delete/<int:id>")
def delete_devocional(id):
    if "admin" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM devocionais WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

# --- Página Sobre ---
@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
