{
    'name': 'Project Discord Mention',
    'version': '19.0.1.0.0',
    'category': 'Project',
    'summary': 'Auto-mention Discord user when task is assigned — Odoo 19 x Discord Webhook integration',
    'description': """
Project Discord Mention
========================
Automatically send a Discord mention to the assigned user(s) every time a task
is assigned or re-assigned in Odoo Project.

Key Features:
- Auto-send Discord notification when task.user_ids changes
- Direct mention using each user's numeric Discord ID
- Multi-assign support — all assignees mentioned in one message
- Message includes: task name, project, deadline, and priority
- Webhook URL stored securely as System Parameter (admin-only)
- No cron job needed — triggers natively via ORM override
    """,
    'author': 'Dody Ahmad Kusuma Jaya',
    'website': 'https://profile.dodyakj.online',
    'license': 'OPL-1',
    'price': 0.00,
    'currency': 'USD',
    'depends': ['project', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
        'views/project_task_views.xml',
        'data/ir_config_parameter.xml',
    ],
    'images': [
        'static/description/odoo_discord_mention.gif',
        'static/description/sc_discord_user_id.png',
        'static/description/sc_webhook_config.png',
        'static/description/sc_task_send_discord.png',
        'static/description/index.html',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 0,
}
