from odoo import api, fields, models, tools, SUPERUSER_ID,_
from io import StringIO
from tempfile import TemporaryFile
import base64
import csv
from odoo.exceptions import UserError, ValidationError



class ImportRole(models.TransientModel):
    _name = 'import.role'

    upload_file = fields.Binary(string='LOAD FILE')

    def import_roles(self):
        csv_datas = self.upload_file
        fileobj = TemporaryFile('wb+')
        csv_datas = base64.decodestring(csv_datas)
        fileobj.write(csv_datas)
        fileobj.seek(0)
        str_csv_data = fileobj.read().decode('utf-8')
        lis = csv.reader(StringIO(str_csv_data), delimiter=',')
        lis_length = csv.reader(StringIO(str_csv_data), delimiter=',')
        create_records_role = 0
        create_records_objective=0
        create_records_role_mapping=0
        create_records_okr_master=0
        collect_records_objective = []
        collect_keys = []
        counter_records_scanned=0
        length_records=len(list(lis_length))
        for row in lis:
            print(row[0])
            print(row[1])
            print(row[2])
            if row[0]:
                if collect_records_objective:
                    lines = []
                    for rec in collect_records_objective:
                        if collect_keys:
                            create_records_objective.write({
                                'key_skill_many': [(6, 0, collect_keys)]
                            })
                        val = {
                            'role_assign_line': rec.id,
                            'key_skill_many_role': rec.key_skill_many.ids
                        }
                        lines.append([0, 0, val])
                    check_records_role_mapping = self.env['role.mapping'].search([('roles_assign','=', create_records_role.name)])
                    check_records_okr_master = self.env['okr.master'].search([('roles_assign_mapp','=', create_records_role.name)])
                    print(check_records_okr_master)
                    if not check_records_role_mapping:
                        create_records_role_mapping = self.env['role.mapping'].create({
                            'roles_assign': create_records_role.id,
                            'objectives_assign':lines
                        })
                        if not check_records_okr_master:
                            create_records_okr_master= self.env['okr.master'].create({
                                'roles_assign_mapp': create_records_role_mapping.id,
                                'okr_mapp_role': lines
                            })
                            print(create_records_okr_master)
                        print(create_records_role_mapping)
                    collect_records_objective.clear()
                    collect_keys.clear()
                check_records_role = self.env['access.rights.master'].search([('name', '=',row[0])])
                if not check_records_role:
                    create_records_role = self.env['access.rights.master'].create({
                        'name': row[0]
                    })
                    print(create_records_role)
            if row[1]:
                if collect_keys:
                    create_records_objective.write({
                        'key_skill_many':[(6, 0,collect_keys)]
                    })
                collect_keys.clear()
                check_records_objective = self.env['objective.master'].search([('objective_name', '=', row[1])])
                if not check_records_objective:
                    create_records_objective = self.env['objective.master'].create({
                        'objective_name': row[1]
                    })
                    collect_records_objective.append(create_records_objective)
                else:
                    collect_records_objective.append(check_records_objective)
                    print(create_records_objective)
            if row[2]:
                check_records_keys = self.env['key.results'].search([('key_skills', '=', row[2])])
                if not check_records_keys:
                    create_records_key = self.env['key.results'].create({
                        'key_skills': row[2]
                    }).id
                    collect_keys.append(create_records_key)
                    print(create_records_key)
                    counter_records_scanned+=1

                else:
                    collect_keys.append(check_records_keys.id)
                    counter_records_scanned+=1
                if counter_records_scanned == length_records:
                    if collect_records_objective:
                        lines = []
                        for rec in collect_records_objective:
                            if collect_keys:
                                create_records_objective.write({
                                    'key_skill_many': [(6, 0, collect_keys)]
                                })
                            val = {
                                'role_assign_line': rec.id,
                                'key_skill_many_role': rec.key_skill_many.ids
                            }
                            lines.append([0, 0, val])
                        check_records_role_mapping = self.env['role.mapping'].search(
                            [('roles_assign', '=', create_records_role.name)])
                        check_records_okr_master = self.env['okr.master'].search(
                            [('roles_assign_mapp', '=', create_records_role.name)])
                        if not check_records_role_mapping:
                            create_records_role_mapping = self.env['role.mapping'].create({
                                'roles_assign': create_records_role.id,
                                'objectives_assign': lines
                            })
                            if not check_records_okr_master:
                                create_records_okr_master = self.env['okr.master'].create({
                                    'roles_assign_mapp': create_records_role_mapping.id,
                                    'okr_mapp_role': lines
                                })
                                print(create_records_okr_master)
                            print(create_records_role_mapping)
                        collect_records_objective.clear()
                        collect_keys.clear()



