# -*- coding: utf-8 -*-
"""actualizar_json.py - Anade cadenas faltantes al JSON."""
import json
import shutil
from pathlib import Path

BASE = Path(r"E:\02_proyectos\Redaccion_castellana_curso-main")
JSON_FILE = BASE / "traducciones.json"


def backup(ruta):
    bak = ruta.with_suffix(ruta.suffix + ".bak")
    if not bak.exists():
        shutil.copy2(ruta, bak)


NUEVAS = {
    "1000 técnicas de redacción": {
        "es": "1000 técnicas de redacción", "en": "1000 writing techniques",
        "zh_Hans": "1000 种写作技巧", "hi": "1000 लेखन तकनीकें",
        "ar": "1000 تقنية كتابة", "fr": "1000 techniques d'écriture",
        "pt": "1000 técnicas de redação", "ru": "1000 техник письма",
        "bn": "1000টি লেখার কৌশল", "ur": "1000 تحریری تکنیکیں",
        "ja": "1000のライティングテクニック", "de": "1000 Schreibtechniken",
        "ko": "1000가지 작문 기법", "it": "1000 tecniche di scrittura",
        "tr": "1000 yazma tekniği", "vi": "1000 kỹ thuật viết"
    },
    "Archivo de Vector": {
        "es": "Archivo de Vector", "en": "Vector Archive",
        "zh_Hans": "矢量档案", "hi": "वेक्टर संग्रह",
        "ar": "أرشيف المتجهات", "fr": "Archives Vector",
        "pt": "Arquivo de Vetor", "ru": "Архив векторов",
        "bn": "ভেক্টর আর্কাইভ", "ur": "ویکٹر آرکائیو",
        "ja": "ベクターアーカイブ", "de": "Vektor-Archiv",
        "ko": "벡터 아카이브", "it": "Archivio Vettoriale",
        "tr": "Vektör Arşivi", "vi": "Kho lưu trữ Vector"
    },
    "Registro": {
        "es": "Registro", "en": "Sign up", "zh_Hans": "注册",
        "hi": "साइन अप", "ar": "التسجيل", "fr": "Inscription",
        "pt": "Registro", "ru": "Регистрация", "bn": "সাইন আপ",
        "ur": "رجسٹریشن", "ja": "登録", "de": "Registrieren",
        "ko": "가입", "it": "Registrati", "tr": "Kayıt ol", "vi": "Đăng ký"
    },
    "Mi progreso": {
        "es": "Mi progreso", "en": "My progress", "zh_Hans": "我的进度",
        "hi": "मेरी प्रगति", "ar": "تقدمي", "fr": "Mes progrès",
        "pt": "Meu progresso", "ru": "Мой прогресс", "bn": "আমার অগ্রগতি",
        "ur": "میری پیش رفت", "ja": "私の進捗", "de": "Mein Fortschritt",
        "ko": "내 진행 상황", "it": "I miei progressi", "tr": "İlerlemem",
        "vi": "Tiến độ của tôi"
    },
    "Salir": {
        "es": "Salir", "en": "Log out", "zh_Hans": "退出",
        "hi": "लॉग आउट", "ar": "تسجيل الخروج", "fr": "Déconnexion",
        "pt": "Sair", "ru": "Выйти", "bn": "লগ আউট",
        "ur": "لاگ آؤٹ", "ja": "ログアウト", "de": "Abmelden",
        "ko": "로그아웃", "it": "Esci", "tr": "Çıkış yap", "vi": "Đăng xuất"
    },
    "No tienes cuenta?": {
        "es": "¿No tienes cuenta?", "en": "Don't have an account?",
        "zh_Hans": "还没有账户？", "hi": "खाता नहीं है?",
        "ar": "ليس لديك حساب؟", "fr": "Vous n'avez pas de compte ?",
        "pt": "Não tem uma conta?", "ru": "Нет аккаунта?",
        "bn": "অ্যাকাউন্ট নেই?", "ur": "اکاؤنٹ نہیں ہے؟",
        "ja": "アカウントをお持ちでないですか？", "de": "Kein Konto?",
        "ko": "계정이 없으신가요?", "it": "Non hai un account?",
        "tr": "Hesabınız yok mu?", "vi": "Chưa có tài khoản?"
    },
    "Ya tienes cuenta?": {
        "es": "¿Ya tienes cuenta?", "en": "Already have an account?",
        "zh_Hans": "已有账户？", "hi": "क्या आपके पास पहले से खाता है?",
        "ar": "هل لديك حساب بالفعل؟", "fr": "Vous avez déjà un compte ?",
        "pt": "Já tem uma conta?", "ru": "Уже есть аккаунт?",
        "bn": "ইতিমধ্যে একটি অ্যাকাউন্ট আছে?", "ur": "پہلے سے اکاؤنٹ ہے؟",
        "ja": "すでにアカウントをお持ちですか？", "de": "Haben Sie schon ein Konto?",
        "ko": "이미 계정이 있으신가요?", "it": "Hai già un account?",
        "tr": "Zaten hesabınız var mı?", "vi": "Đã có tài khoản?"
    },
    "Registrate": {
        "es": "Regístrate", "en": "Sign up", "zh_Hans": "注册",
        "hi": "साइन अप करें", "ar": "سجل", "fr": "Inscrivez-vous",
        "pt": "Registre-se", "ru": "Зарегистрируйтесь", "bn": "নিবন্ধন করুন",
        "ur": "رجسٹر کریں", "ja": "登録する", "de": "Registrieren",
        "ko": "가입하기", "it": "Registrati", "tr": "Kayıt ol", "vi": "Đăng ký"
    },
    "Inicia sesion": {
        "es": "Inicia sesión", "en": "Log in", "zh_Hans": "登录",
        "hi": "लॉग इन करें", "ar": "تسجيل الدخول", "fr": "Connexion",
        "pt": "Inicie sessão", "ru": "Войти", "bn": "লগ ইন করুন",
        "ur": "لاگ ان کریں", "ja": "ログイン", "de": "Anmelden",
        "ko": "로그인", "it": "Accedi", "tr": "Giriş yap", "vi": "Đăng nhập"
    },
    "Correo electronico": {
        "es": "Correo electrónico", "en": "Email", "zh_Hans": "电子邮件",
        "hi": "ईमेल", "ar": "البريد الإلكتروني", "fr": "E-mail",
        "pt": "E-mail", "ru": "Электронная почта", "bn": "ইমেল",
        "ur": "ای میل", "ja": "メールアドレス", "de": "E-Mail",
        "ko": "이메일", "it": "Email", "tr": "E-posta", "vi": "Email"
    },
    "Contrasena": {
        "es": "Contraseña", "en": "Password", "zh_Hans": "密码",
        "hi": "पासवर्ड", "ar": "كلمة المرور", "fr": "Mot de passe",
        "pt": "Senha", "ru": "Пароль", "bn": "পাসওয়ার্ড",
        "ur": "پاس ورڈ", "ja": "パスワード", "de": "Passwort",
        "ko": "비밀번호", "it": "Password", "tr": "Şifre", "vi": "Mật khẩu"
    },
    "Entrar": {
        "es": "Entrar", "en": "Log in", "zh_Hans": "登录",
        "hi": "लॉग इन", "ar": "تسجيل الدخول", "fr": "Connexion",
        "pt": "Entrar", "ru": "Войти", "bn": "লগ ইন",
        "ur": "لاگ ان", "ja": "ログイン", "de": "Anmelden",
        "ko": "로그인", "it": "Accedi", "tr": "Giriş yap", "vi": "Đăng nhập"
    },
    "Crear cuenta": {
        "es": "Crear cuenta", "en": "Create account", "zh_Hans": "创建账户",
        "hi": "खाता बनाएँ", "ar": "إنشاء حساب", "fr": "Créer un compte",
        "pt": "Criar conta", "ru": "Создать аккаунт", "bn": "অ্যাকাউন্ট তৈরি করুন",
        "ur": "اکاؤنٹ بنائیں", "ja": "アカウント作成", "de": "Konto erstellen",
        "ko": "계정 만들기", "it": "Crea account", "tr": "Hesap oluştur",
        "vi": "Tạo tài khoản"
    },
    "Volver a Cursos": {
        "es": "Volver a Cursos", "en": "Back to Courses", "zh_Hans": "返回课程",
        "hi": "पाठ्यक्रमों पर वापस", "ar": "العودة إلى الدورات",
        "fr": "Retour aux cours", "pt": "Voltar aos Cursos",
        "ru": "Назад к курсам", "bn": "কোর্সে ফিরে যান", "ur": "کورسز پر واپس",
        "ja": "コースに戻る", "de": "Zurück zu den Kursen",
        "ko": "코스로 돌아가기", "it": "Torna ai corsi",
        "tr": "Kurslara dön", "vi": "Quay lại khóa học"
    },
    "Inscribirse al curso": {
        "es": "Inscribirse al curso", "en": "Enroll in course",
        "zh_Hans": "报名参加课程", "hi": "कोर्स में नामांकन करें",
        "ar": "التسجيل في الدورة", "fr": "S'inscrire au cours",
        "pt": "Inscrever-se no curso", "ru": "Записаться на курс",
        "bn": "কোর্সে ভর্তি হন", "ur": "کورس میں داخلہ لیں",
        "ja": "コースに登録", "de": "Für den Kurs anmelden",
        "ko": "코스 등록", "it": "Iscriviti al corso",
        "tr": "Kursa kaydol", "vi": "Đăng ký khóa học"
    },
    "Explora los cursos disponibles": {
        "es": "Explora los cursos disponibles", "en": "Explore available courses",
        "zh_Hans": "探索可用课程", "hi": "उपलब्ध पाठ्यक्रमों का अन्वेषण करें",
        "ar": "استكشف الدورات المتاحة", "fr": "Explorez les cours disponibles",
        "pt": "Explore os cursos disponíveis", "ru": "Изучите доступные курсы",
        "bn": "উপলব্ধ কোর্সগুলি অন্বেষণ করুন", "ur": "دستیاب کورسز کو دریافت کریں",
        "ja": "利用可能なコースを探す", "de": "Verfügbare Kurse erkunden",
        "ko": "사용 가능한 코스 탐색", "it": "Esplora i corsi disponibili",
        "tr": "Mevcut kursları keşfet", "vi": "Khám phá các khóa học có sẵn"
    },
    "Todos los recursos disponibles": {
        "es": "Todos los recursos disponibles", "en": "All available resources",
        "zh_Hans": "所有可用资源", "hi": "सभी उपलब्ध संसाधन",
        "ar": "جميع الموارد المتاحة", "fr": "Toutes les ressources disponibles",
        "pt": "Todos os recursos disponíveis", "ru": "Все доступные ресурсы",
        "bn": "সমস্ত উপলব্ধ সম্পদ", "ur": "تمام دستیاب وسائل",
        "ja": "利用可能なすべてのリソース", "de": "Alle verfügbaren Ressourcen",
        "ko": "사용 가능한 모든 리소스", "it": "Tutte le risorse disponibili",
        "tr": "Mevcut tüm kaynaklar", "vi": "Tất cả tài nguyên có sẵn"
    },
    "No hay cursos disponibles": {
        "es": "No hay cursos disponibles", "en": "No courses available",
        "zh_Hans": "没有可用的课程", "hi": "कोई पाठ्यक्रम उपलब्ध नहीं",
        "ar": "لا توجد دورات متاحة", "fr": "Aucun cours disponible",
        "pt": "Nenhum curso disponível", "ru": "Нет доступных курсов",
        "bn": "কোনও কোর্স উপলব্ধ নেই", "ur": "کوئی کورس دستیاب نہیں",
        "ja": "利用可能なコースはありません", "de": "Keine Kurse verfügbar",
        "ko": "사용 가능한 코스 없음", "it": "Nessun corso disponibile",
        "tr": "Mevcut kurs yok", "vi": "Không có khóa học"
    },
    "No hay lecciones disponibles": {
        "es": "No hay lecciones disponibles", "en": "No lessons available",
        "zh_Hans": "没有可用的课程", "hi": "कोई पाठ उपलब्ध नहीं",
        "ar": "لا توجد دروس متاحة", "fr": "Aucune leçon disponible",
        "pt": "Nenhuma lição disponível", "ru": "Нет доступных уроков",
        "bn": "কোনও পাঠ উপলব্ধ নেই", "ur": "کوئی سبق دستیاب نہیں",
        "ja": "利用可能なレッスンはありません", "de": "Keine Lektionen verfügbar",
        "ko": "사용 가능한 레슨 없음", "it": "Nessuna lezione disponibile",
        "tr": "Mevcut ders yok", "vi": "Không có bài học"
    },
    "No hay recursos disponibles": {
        "es": "No hay recursos disponibles", "en": "No resources available",
        "zh_Hans": "没有可用的资源", "hi": "कोई संसाधन उपलब्ध नहीं",
        "ar": "لا توجد موارد متاحة", "fr": "Aucune ressource disponible",
        "pt": "Nenhum recurso disponível", "ru": "Нет доступных ресурсов",
        "bn": "কোনও সম্পদ উপলব্ধ নেই", "ur": "کوئی وسیلہ دستیاب نہیں",
        "ja": "利用可能なリソースはありません", "de": "Keine Ressourcen verfügbar",
        "ko": "사용 가능한 리소스 없음", "it": "Nessuna risorsa disponibile",
        "tr": "Mevcut kaynak yok", "vi": "Không có tài nguyên"
    },
    "Lecciones": {
        "es": "Lecciones", "en": "Lessons", "zh_Hans": "课程",
        "hi": "पाठ", "ar": "الدروس", "fr": "Leçons",
        "pt": "Lições", "ru": "Уроки", "bn": "পাঠ",
        "ur": "اسباق", "ja": "レッスン", "de": "Lektionen",
        "ko": "레슨", "it": "Lezioni", "tr": "Dersler", "vi": "Bài học"
    },
    "lecciones": {
        "es": "lecciones", "en": "lessons", "zh_Hans": "课程",
        "hi": "पाठ", "ar": "دروس", "fr": "leçons",
        "pt": "lições", "ru": "уроков", "bn": "পাঠ",
        "ur": "اسباق", "ja": "レッスン", "de": "Lektionen",
        "ko": "레슨", "it": "lezioni", "tr": "ders", "vi": "bài học"
    },
    "Practicar": {
        "es": "Practicar", "en": "Practice", "zh_Hans": "练习",
        "hi": "अभ्यास", "ar": "ممارسة", "fr": "Pratiquer",
        "pt": "Praticar", "ru": "Практика", "bn": "অনুশীলন",
        "ur": "مشق", "ja": "練習", "de": "Üben",
        "ko": "연습", "it": "Esercitati", "tr": "Alıştırma yap", "vi": "Luyện tập"
    },
    "Inscribirse": {
        "es": "Inscribirse", "en": "Enroll", "zh_Hans": "报名",
        "hi": "नामांकन करें", "ar": "التسجيل", "fr": "S'inscrire",
        "pt": "Inscrever-se", "ru": "Записаться", "bn": "ভর্তি হন",
        "ur": "داخلہ لیں", "ja": "登録", "de": "Anmelden",
        "ko": "등록", "it": "Iscriviti", "tr": "Kaydol", "vi": "Đăng ký"
    },
    "Usuario": {
        "es": "Usuario", "en": "User", "zh_Hans": "用户",
        "hi": "उपयोगकर्ता", "ar": "المستخدم", "fr": "Utilisateur",
        "pt": "Usuário", "ru": "Пользователь", "bn": "ব্যবহারকারী",
        "ur": "صارف", "ja": "ユーザー", "de": "Benutzer",
        "ko": "사용자", "it": "Utente", "tr": "Kullanıcı", "vi": "Người dùng"
    },
    "Cronista Temporal": {
        "es": "Cronista Temporal", "en": "Time Chronicler",
        "zh_Hans": "时间编年史家", "hi": "समय इतिहासकार",
        "ar": "مؤرخ الزمن", "fr": "Chroniqueur Temporel",
        "pt": "Cronista Temporal", "ru": "Временной хронист",
        "bn": "সময়ের ক্রনিকলার", "ur": "وقت کا وقائع نگار",
        "ja": "時のクロニスタ", "de": "Zeitchronist",
        "ko": "시간 기록자", "it": "Cronista Temporale",
        "tr": "Zaman Tarihçisi", "vi": "Biên niên sử thời gian"
    },
}
def main():
    print("ACTUALIZAR JSON")
    if not JSON_FILE.exists():
        print("ERROR: no existe JSON")
        return
    backup(JSON_FILE)
    with JSON_FILE.open(encoding="utf-8-sig") as f:
        datos = json.load(f)
    print("Antes: " + str(len(datos)) + " cadenas")
    nuevos = 0
    for clave, valor in NUEVAS.items():
        if clave not in datos:
            datos[clave] = valor
            nuevos += 1
    print("Nuevas anadidas: " + str(nuevos))
    with JSON_FILE.open("w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print("Despues: " + str(len(datos)) + " cadenas")
    print("LISTO")


if __name__ == "__main__":
    main()
