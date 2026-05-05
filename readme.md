# 🎯 Odoo 19 — Discord Task Mention Integration

> Custom Addons untuk Odoo 19 yang secara otomatis mengirim mention Discord ketika task di-assign ke user.

---

## 📌 Fitur Utama

- ✅ Otomatis kirim notifikasi ke Discord channel saat task di-assign
- ✅ Mention langsung ke user Discord berdasarkan ID yang terdaftar
- ✅ Mendukung multi-assign (mention semua user yang di-assign sekaligus)
- ✅ Konfigurasi Webhook Discord per project atau global
- ✅ Tampilkan detail task: nama task, project, deadline, dan prioritas
- ✅ Integrasi penuh dengan modul `project.task` Odoo 19

---

## 🧩 Struktur Modul

```
project_discord_mention/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── res_users.py          # Tambah field discord_user_id ke res.users
│   └── project_task.py       # Override assign task → trigger Discord
├── views/
│   ├── res_users_views.xml   # Form view tambahan field Discord ID
│   └── project_task_views.xml
├── data/
│   └── ir_config_parameter.xml  # Default config webhook
├── security/
│   └── ir.model.access.csv
└── README.md
```

---

## ⚙️ Persyaratan Sistem

| Komponen | Versi |
|----------|-------|
| Odoo | 19.0 |
| Python | 3.11+ |
| Library | `requests` |
| Discord | Bot / Webhook aktif |

---

## 🚀 Instalasi

### 1. Clone atau Copy Modul

```bash
git clone https://github.com/username/project_discord_mention.git
# atau copy folder ke direktori addons Odoo
cp -r project_discord_mention/ /odoo/custom-addons/
```

### 2. Update `odoo.conf`

Tambahkan path addons custom ke konfigurasi Odoo:

```ini
[options]
addons_path = /odoo/addons,/odoo/custom-addons
```

### 3. Install Dependensi Python

```bash
pip install requests
```

### 4. Restart & Install Modul

```bash
# Restart service Odoo
sudo systemctl restart odoo

# Atau via CLI
python odoo-bin -c odoo.conf -u project_discord_mention --stop-after-init
```

Kemudian masuk ke **Apps → Search "Discord Mention" → Install**.

---

## 🔧 Konfigurasi

### Step 1 — Buat Discord Webhook

1. Buka Discord Server → Channel yang dituju
2. **Edit Channel → Integrations → Webhooks → New Webhook**
3. Copy **Webhook URL**

### Step 2 — Simpan Webhook di Odoo

Masuk ke:
> **Settings → Technical → Parameters → System Parameters**

Tambahkan key:

| Key | Value |
|-----|-------|
| `discord.webhook.url` | `https://discord.com/api/webhooks/xxx/yyy` |

> 💡 Bisa juga dikonfigurasi per-project melalui form Project jika menggunakan field webhook per project.

### Step 3 — Isi Discord User ID di Profil User

1. Masuk ke **Settings → Users & Companies → Users**
2. Pilih user → Tab **Discord**
3. Isi field **Discord User ID**

**Cara mendapatkan Discord User ID:**
- Aktifkan Developer Mode di Discord (Settings → Advanced → Developer Mode)
- Klik kanan nama user → **Copy User ID**

---

## 💻 Kode Inti

### `models/res_users.py`

```python
from odoo import fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    discord_user_id = fields.Char(
        string='Discord User ID',
        help='ID numerik akun Discord user (aktifkan Developer Mode di Discord)'
    )
```

### `models/project_task.py`

```python
import requests
from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        for task in tasks:
            if task.user_ids:
                task._send_discord_mention()
        return tasks

    def write(self, vals):
        res = super().write(vals)
        if 'user_ids' in vals:
            for task in self:
                if task.user_ids:
                    task._send_discord_mention()
        return res

    def _send_discord_mention(self):
        webhook_url = self.env['ir.config_parameter'].sudo().get_param(
            'discord.webhook.url'
        )
        if not webhook_url:
            _logger.warning('Discord webhook URL belum dikonfigurasi.')
            return

        mentions = []
        for user in self.user_ids:
            if user.discord_user_id:
                mentions.append(f'<@{user.discord_user_id}>')

        mention_str = ' '.join(mentions) if mentions else '*(tidak ada Discord ID terdaftar)*'

        deadline_str = self.date_deadline.strftime('%d %B %Y') if self.date_deadline else 'Tidak ada'
        priority_map = {'0': '🟢 Normal', '1': '🔴 Urgent'}
        priority_str = priority_map.get(self.priority, '🟢 Normal')

        payload = {
            "content": f"📋 **Task Baru Assigned!**\n\n"
                       f"👤 Assigned to: {mention_str}\n"
                       f"📝 Task: **{self.name}**\n"
                       f"📁 Project: **{self.project_id.name if self.project_id else '-'}**\n"
                       f"📅 Deadline: **{deadline_str}**\n"
                       f"⚡ Prioritas: {priority_str}\n\n"
                       f"🔗 Cek task di Odoo untuk detail lengkap."
        }

        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            _logger.info(f'Discord notification sent for task: {self.name}')
        except requests.exceptions.RequestException as e:
            _logger.error(f'Gagal mengirim notifikasi Discord: {e}')
```

### `__manifest__.py`

```python
{
    'name': 'Project Discord Mention',
    'version': '19.0.1.0.0',
    'category': 'Project',
    'summary': 'Auto mention Discord user saat task di-assign',
    'description': """
        Integrasi Odoo Project dengan Discord.
        Kirim mention otomatis ke user Discord saat task di-assign.
    """,
    'author': 'Your Name',
    'website': 'https://github.com/username/project_discord_mention',
    'license': 'LGPL-3',
    'depends': ['project', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
        'views/project_task_views.xml',
        'data/ir_config_parameter.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
```

---

## 📣 Contoh Output Notifikasi Discord

```
📋 Task Baru Assigned!

👤 Assigned to: @BudiSantoso @AnisaRahayu
📝 Task: Implementasi Fitur Login SSO
📁 Project: Website Revamp Q3
📅 Deadline: 25 Juli 2025
⚡ Prioritas: 🔴 Urgent

🔗 Cek task di Odoo untuk detail lengkap.
```

---

## 🛡️ Keamanan & Catatan Penting

- 🔐 Webhook URL disimpan sebagai **System Parameter** (hanya admin yang bisa akses)
- ⚠️ Jangan pernah hardcode Webhook URL langsung di kode Python
- 📌 Discord User ID bersifat **numerik**, pastikan tidak salah salin
- 🚫 Jika user tidak memiliki Discord ID, notifikasi tetap terkirim tanpa mention
- 🔁 Notifikasi dikirim setiap kali field `user_ids` berubah (termasuk re-assign)

---

## 🐛 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Notifikasi tidak terkirim | Cek webhook URL di System Parameters |
| Mention tidak muncul | Pastikan Discord User ID sudah diisi dan benar |
| Error `requests` not found | Jalankan `pip install requests` |
| 404 dari Discord | Webhook mungkin sudah dihapus, buat ulang |
| Log error di Odoo | Cek `/var/log/odoo/odoo.log` untuk detail |

---

## 📝 Changelog

### v19.0.1.0.0 (Initial Release)
- 🎉 Rilis pertama
- Fitur auto-mention saat task di-assign
- Konfigurasi Discord ID per user
- Support multi-user assign
- Integrasi webhook Discord

---

## 🤝 Kontribusi

Pull request sangat disambut! Untuk perubahan besar, harap buka Issue terlebih dahulu untuk diskusi.

1. Fork repository
2. Buat branch fitur (`git checkout -b feature/nama-fitur`)
3. Commit perubahan (`git commit -m 'feat: tambah fitur X'`)
4. Push ke branch (`git push origin feature/nama-fitur`)
5. Buka Pull Request

---

## 📄 Lisensi

Modul ini dilisensikan di bawah [LGPL-3](https://www.gnu.org/licenses/lgpl-3.0.html) — bebas digunakan dan dimodifikasi.

---

<div align="center">
  Made with ❤️ for Odoo 19 Community
</div>