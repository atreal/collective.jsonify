from collective.jsonify.wrapper import Wrapper
import os

class SpeedWrapper(Wrapper):
    """ """

    def get_archetypes_fields(self):
        """ If Archetypes is used then dump schema
        """

        try:
            from Products.Archetypes.interfaces import IBaseObject
            if not IBaseObject.providedBy(self.context):
                return
        except:
            return

        import base64
        fields = self.context.schema.fields()
        for field in fields:
            fieldname = unicode(field.__name__)
            type_ = field.__class__.__name__

            fieldnames = [
                'StringField', 'BooleanField', 'LinesField',
                'IntegerField', 'TextField', 'SimpleDataGridField',
                'FloatField', 'FixedPointField', 'TALESString',
                'TALESLines', 'ZPTField', 'DataGridField', 'EmailField',
                'QueryField',
            ]

            if type_ in fieldnames:
                try:
                    value = field.getRaw(self.context)
                except AttributeError:
                    value = self._get_at_field_value(field)

                if callable(value) is True:
                    value = value()

                if value and type_ in ['StringField', 'TextField']:
                    try:
                        value = self.decode(value)
                    except AttributeError:
                        # maybe an int?
                        value = unicode(value)
                    except Exception, e:
                        raise Exception('problems with %s: %s' % (
                            self.context.absolute_url(), str(e))
                        )
                elif value and type_ == 'DataGridField':
                    for i, row in enumerate(value):
                        for col_key in row.keys():
                            col_value = row[col_key]
                            if type(col_value) in (unicode, str):
                                value[i][col_key] = self.decode(col_value)

                try:
                    ct = field.getContentType(self.context)
                except AttributeError:
                    ct = ''
                self[unicode(fieldname)] = value
                self[unicode('_content_type_') + fieldname] = ct

            elif type_ in ['DateTimeField']:
                value = str(self._get_at_field_value(field))
                if value:
                    self[unicode(fieldname)] = value

            elif type_ in ['ImageField', 'FileField', 'AttachmentField']:
                fieldname = unicode('_datafield_' + fieldname)

                value = self._get_at_field_value(field)
                value2 = value

                if type(value) is not str:
                    if type(value.data) is str:
                        value = base64.b64encode(value.data)
                    else:
                        data = value.data
                        value = ''
                        while data is not None:
                            value += data.data
                            data = data.next
                        value = base64.b64encode(value)




                try:
                    max_filesize = int(
                        os.environ.get('JSONIFY_MAX_FILESIZE', 20000000)
                    )
                except ValueError:
                    max_filesize = 20000000

                if value and len(value) < max_filesize:
                    size = value2.getSize()
                    try:
                        fname = field.getFilename(self.context)
                    except AttributeError:
                        fname = value2.getFilename()

                    try:
                        fname = self.decode(fname)
                    except AttributeError:
                        # maybe an int?
                        fname = unicode(fname)
                    except Exception, e:
                        raise Exception(
                            'problems with %s: %s' % (
                                self.context.absolute_url(), str(e)
                            )
                        )

                    try:
                        ctype = field.getContentType(self.context)
                    except AttributeError:
                        ctype = value2.getContentType()

                    self[fieldname] = {
                        'data': value,
                        'size': size,
                        'filename': fname or '',
                        'content_type': ctype
                    }

            elif type_ in ['ReferenceField']:
                pass

            elif type_ in ['ComputedField']:
                continue

            elif type_ in ['BlobFileField']:
                fieldname = unicode('_datafield_' + fieldname)

                value = self._get_at_field_value(field)
                value2 = value

                if type(value) is not str:
                    blobdata = value.data.open().read()
                    if type(blobdata) is str:
                        value = base64.b64encode(blobdata)
                    else:
                        data = value.data
                        value = ''
                        while data is not None:
                            value += data.data
                            data = data.next
                        value = base64.b64encode(value)




                try:
                    max_filesize = int(
                        os.environ.get('JSONIFY_MAX_FILESIZE', 20000000)
                    )
                except ValueError:
                    max_filesize = 20000000

                if value and len(value) < max_filesize:
                    size = value2.getSize()
                    try:
                        fname = field.getFilename(self.context)
                    except AttributeError:
                        fname = value2.getFilename()

                    try:
                        fname = self.decode(fname)
                    except AttributeError:
                        # maybe an int?
                        fname = unicode(fname)
                    except Exception, e:
                        raise Exception(
                            'problems with %s: %s' % (
                                self.context.absolute_url(), str(e)
                            )
                        )

                    try:
                        ctype = field.getContentType(self.context)
                    except AttributeError:
                        ctype = value2.getContentType()

                    self[fieldname] = {
                        'data': value,
                        'size': size,
                        'filename': fname or '',
                        'content_type': ctype
                    }


            else:
                import ipdb; ipdb.set_trace()
                raise TypeError('SPEED Unknown field type for ArchetypesWrapper in '
                        '%s in %s' % (fieldname, self.context.absolute_url()))


    def get_format(self):
        """ Format of object
            :keys: _format
        """
        if self['_classname'] == 'ULink':
            self['_content_type'] = 'text/plain'
        else:
            self['_content_type'] = self.context.Format()

