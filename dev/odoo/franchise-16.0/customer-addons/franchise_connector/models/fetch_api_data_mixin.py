from odoo import models, api, fields
from . import api_exceptions
import xmlrpc.client


class FetchApiDataMixin(models.AbstractModel):
    _name = 'franchise.data.fetch.mixin'
    _description = 'Mixin that contains utility methods for API data fetching'

    DB = fields.Char()
    USERNAME = fields.Char()
    PASSWORD = fields.Char()
    URL = fields.Char()
    API_KEY = fields.Char()

    @api.model
    def set_auth_data(self, db, username, password, url, api_key):
        """
        Set the authentication data used for API connection.

        :param db: The name of the database.
        :param username: The username for authentication.
        :param password: The password for authentication.
        :param url: The URL of the Odoo instance.
        :param api_key: The API key used for authentication.
        """
        self.DB = db
        self.USERNAME = username
        self.PASSWORD = password
        self.URL = url
        self.API_KEY = api_key

    def fetch_data(self, model):
        """
        Fetch data from the specified model via the Odoo API.

        :param model: The name of the Odoo model to fetch data from.
        :return: The fetched data as a list of dictionaries, or None if an error occurs.
        """
        # Odoo common endpoint for XML-RPC
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.URL))

        # Authenticate and get user ID
        uid = common.authenticate(self.DB, self.USERNAME, self.PASSWORD, {})

        # Odoo object endpoint for XML-RPC
        record_models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.URL))
        try:
            data = record_models.execute_kw(self.DB, uid, self.API_KEY, model, 'search_read', [])
            return data
        except Exception as e:
            raise api_exceptions.FetchDataError(f"Failed to fetch data for model '{model}': {e}")

    def save_data(self, model, data, excluded_models=[]):
        """
        Save the data received from the API into the specified Odoo model.
        :param model: The name of the Odoo model to save data into.
        :param data: The data to be saved, typically a list of dictionaries where each dictionary represents a record.
        """
        # Ensure the model exists in the environment
        if model not in self.env:
            raise api_exceptions.SaveDataError(f"Model '{model}' not found in the environment.")

        # Save model data
        record_model = self.env[model]
        print(f"Saving model: {model}")

        # We need to filter fields because our instance may not have the same modules installed
        # we are just keeping those fields we can use

        model_fields = record_model.fields_get()

        excluded_fields = {}

        # filter undesired model fields
        for ex_model in excluded_models:
            excluded_model = self.env[ex_model]
            excluded_models_fields = excluded_model.fields_get()
            excluded_fields.update(excluded_models_fields)

        for record_data in data:
            # Filter out fields that do not exist in the Franchise instance
            # Also filters undesired fields
            filtered_record_data = {key: record_data[key] for key in record_data if
                                    key in model_fields and key not in excluded_fields}

            # Preprocess fields with list values
            for field, value in filtered_record_data.items():
                if isinstance(value, list) and value:

                    if field.endswith('ids'):
                        filtered_record_data[field] = value
                    else:
                        # Extract the first element from the list
                        filtered_record_data[field] = value[0]

            record = record_model.search([('id', '=', filtered_record_data.get('id'))])  # FIXME possible id conflict
            if record:
                # Attempt to update existing record
                # try:
                record.write(filtered_record_data)
                # except Exception as update_error:
                #     # If update fails (e.g., due to constraint violation), delete existing record and create a new one
                #     # record.unlink()
                #     self.env.cr.rollback()  # Start a new transaction
                #     record.write({'active': False})
                #
                #     self._create_new_record(data, filtered_record_data, record_model)
            else:
                # Create new record

                self._create_new_record(data, filtered_record_data, record_model)

            self.env.cr.commit()  # We might need to commit the changes to the database idk idk

        return True

    def _create_new_record(self, data, record_data, record_model):
        old_record_id = record_data.get('id')
        print(f"old record id: {old_record_id}")

        try:
            new_record = record_model.create(record_data)  # FIXME permission error
        except Exception as e:
            if "Record does not exist" in str(e):
                self._resolve_id_dependencies()


        new_record.write({'original_id': old_record_id})

        print(f"original id: {new_record.original_id}")

        print(f"new record id: {new_record.id}")

        if old_record_id != new_record.id:
            self._fix_related_ids(data)

    def _resolve_id_dependencies(self):

    def synchronize_models(self, record_models, excluded_models=[]):
        """
        Synchronize data for multiple models.

        :param record_models: A list of model names to synchronize data for.
        """
        for model in record_models:
            data = self.fetch_data(model)
            if data is None:
                raise api_exceptions.FetchDataError(f"Failed to fetch data for model '{model}'")

            success = self.save_data(model, data, excluded_models)
            if not success:
                raise api_exceptions.SaveDataError(f"Failed to save data for model '{model}'")

    def _fix_related_ids(self, data):
        for record_data in data:
            for field, value in record_data.items():
                if field.endswith('id') or field.endswith('ids'):
                    # If the value is a list, check and update each element
                    if isinstance(value, list):
                        for i in range(len(value)):
                            if isinstance(value[i], int):
                                value[i] = self._get_original_id(field, value[i])
                    # If the value is a single ID, update it directly
                    elif isinstance(value, int):
                        record_data[field] = self._get_original_id(field, value)

    def _get_original_id(self, field, old_id):
        """Get the corresponding original ID for the given field and old ID."""
        if field == 'product_tmpl_ids':
            model_name = 'product.template'
        else:
            model_name = field.replace('_id', '').replace('_ids', '')
        model = self.env[model_name]
        record = model.search([('original_id', '=', old_id)], limit=1)
        if record:
            return record.id
        else:
            return old_id
