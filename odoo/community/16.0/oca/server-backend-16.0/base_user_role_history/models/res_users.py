# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    last_role_line_modification = fields.Datetime(
        string="Last roles modification", readonly=True
    )

    @api.model
    def _prepare_role_line_history_dict(self, role_line):
        return {
            "user_id": role_line.user_id.id,
            "role_id": role_line.role_id.id,
            "date_from": role_line.date_from,
            "date_to": role_line.date_to,
            "is_enabled": role_line.is_enabled,
        }

    def _get_role_line_values_by_user(self):
        role_line_values_by_user = {}
        for rec in self:
            role_line_values_by_user.setdefault(rec, {})
            for role_line in rec.role_line_ids:
                role_line_values_by_user[rec][
                    role_line.id
                ] = self._prepare_role_line_history_dict(role_line)
        return role_line_values_by_user

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if all("role_line_ids" not in vals for vals in vals_list):
            return res
        new_role_line_values_by_user = res._get_role_line_values_by_user()
        new_role_line_to_create = {}
        users = self.browse()
        for user, lines in new_role_line_values_by_user.items():
            if lines:
                new_role_line_to_create[user] = lines
                user |= user
        self.env["base.user.role.line.history"].create_from_vals(
            {}, new_role_line_to_create
        )
        users.last_role_line_modification = fields.Datetime.now()
        return res

    def write(self, vals):
        if "role_line_ids" not in vals:
            return super().write(vals)
        old_role_line_values_by_user = self._get_role_line_values_by_user()
        vals["last_role_line_modification"] = fields.Datetime.now()
        res = super().write(vals)
        new_role_line_values_by_user = self._get_role_line_values_by_user()
        self.env["base.user.role.line.history"].create_from_vals(
            old_role_line_values_by_user, new_role_line_values_by_user
        )
        return res

    def show_role_lines_history(self):  # pragma: no cover
        self.ensure_one()
        domain = [("user_id", "=", self.id)]
        return {
            "name": _("Roles history"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "base.user.role.line.history",
            "domain": domain,
        }
