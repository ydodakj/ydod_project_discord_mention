import logging
from datetime import datetime, timezone, timedelta

import requests

from odoo import api, models

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
        stage_before = {}
        if 'stage_id' in vals:
            for task in self:
                stage_before[task.id] = task.stage_id

        res = super().write(vals)

        if 'user_ids' in vals:
            for task in self:
                if task.user_ids:
                    task._send_discord_mention()

        if 'stage_id' in vals:
            for task in self:
                old_stage = stage_before.get(task.id)
                if old_stage and old_stage != task.stage_id:
                    task._send_discord_stage_change(old_stage)

        return res

    def action_send_discord(self):
        """Manual trigger dari button di header form task."""
        for task in self:
            task._send_discord_mention()

    def _get_discord_webhook(self):
        webhook_url = self.env['ir.config_parameter'].sudo().get_param('discord.webhook.url')
        if not webhook_url:
            _logger.warning('Discord webhook URL belum dikonfigurasi.')
        return webhook_url

    def _get_mention_str(self):
        mentions = [
            f'<@{user.discord_user_id}>'
            for user in self.user_ids
            if user.discord_user_id
        ]
        return ' '.join(mentions) if mentions else '*(tidak ada Discord User ID terdaftar)*'

    def _now_str(self):
        wib = timezone(timedelta(hours=7))
        return datetime.now(tz=wib).strftime('%d %b %Y %H:%M:%S WIB')

    def _post_to_discord(self, webhook_url, content):
        try:
            response = requests.post(webhook_url, json={'content': content}, timeout=10)
            response.raise_for_status()
            _logger.info('Discord notification sent for task: %s', self.name)
        except requests.exceptions.RequestException as e:
            _logger.error('Gagal mengirim notifikasi Discord: %s', e)

    def _send_discord_mention(self):
        webhook_url = self._get_discord_webhook()
        if not webhook_url:
            return

        mention_str = self._get_mention_str()
        deadline_str = (
            self.date_deadline.strftime('%d %B %Y') if self.date_deadline else 'Tidak ada'
        )
        priority_map = {'0': '🟢 Normal', '1': '🔴 Urgent'}
        priority_str = priority_map.get(self.priority, '🟢 Normal')
        project_name = self.project_id.name if self.project_id else '-'
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        task_url = f'{base_url}/odoo/all-tasks/{self.id}'

        content = (
            f'📋 **Task Assigned!**\n\n'
            f'👤 Assigned to: {mention_str}\n'
            f'📝 Task: **{self.name}**\n'
            f'📁 Project: **{project_name}**\n'
            f'📅 Deadline: **{deadline_str}**\n'
            f'⚡ Prioritas: {priority_str}\n'
            f'🕐 Waktu: **{self._now_str()}**\n\n'
            f'🔗 {task_url}'
        )
        self._post_to_discord(webhook_url, content)

    def _send_discord_stage_change(self, old_stage):
        webhook_url = self._get_discord_webhook()
        if not webhook_url:
            return

        mention_str = self._get_mention_str()
        project_name = self.project_id.name if self.project_id else '-'
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        task_url = f'{base_url}/odoo/all-tasks/{self.id}'

        content = (
            f'🔄 **Stage Task Berubah!**\n\n'
            f'👤 Assigned to: {mention_str}\n'
            f'📝 Task: **{self.name}**\n'
            f'📁 Project: **{project_name}**\n'
            f'📊 Stage: **{old_stage.name}** → **{self.stage_id.name}**\n'
            f'🕐 Waktu: **{self._now_str()}**\n\n'
            f'🔗 {task_url}'
        )
        self._post_to_discord(webhook_url, content)
