# copied from https://stackoverflow.com/questions/750908/auto-repr-method
class AutoRepr(object):
    def __repr__(self):
        items = ("%s = %r" % (k, v) for k, v in self.__dict__.items())
        return "<%s: {%s}>" % (self.__class__.__name__, ', '.join(items))


class ApiException(Exception):
    def __init__(self, **kwargs):
        self.message = kwargs.pop('message')
        self.code = kwargs.pop('code')
        self.data = kwargs.pop('data')

        if self.data:
            super().__init__(f'{self.code}: {self.message}\n' + "\n".join([f'{k}: {v}' for k, v in self.data.items()]))
        else:
            super().__init__(f'{self.code}: {self.message}')


class Nationality(AutoRepr):
    def __init__(self, **kwargs):
        self.nation = kwargs.pop('nation')
        self.country_code = kwargs.pop('country_code')


class User(AutoRepr):
    def __init__(self, etag, **kwargs):
        self.etag = etag

        self.id = kwargs.pop('id')
        self.name = kwargs.pop('name')
        self.permissions = kwargs.pop('permissions')  # TODO: bitmask
        self.display_name = kwargs.pop('display_name')
        self.youtube_channel = kwargs.pop('youtube_channel')


class EmbeddedPlayer(AutoRepr):
    def __init__(self, **kwargs):
        self.id = kwargs.pop('id')
        self.name = kwargs.pop('name')
        self.banned = kwargs.pop('banned')


class ShortPlayer(EmbeddedPlayer):
    def __init__(self, **kwargs):
        self.nationality = kwargs.pop('nationality')

        if self.nationality is not None:
            self.nationality = Nationality(**self.nationality)

        super().__init__(**kwargs)


class ShortDemon(AutoRepr):
    """
    Models both the short and embedded form mentioned in the API
    """

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        self.position = kwargs.pop('position')
        self.publisher = kwargs.get('publisher')
        self.video = kwargs.get('video')


class ShortRecord(AutoRepr):
    """
    Models the embedded form mentioned in the API
    """

    def __init__(self, **kwargs):
        self.id = kwargs.pop('id')
        self.progress = kwargs.pop('progress')
        self.status = kwargs.pop('status')  # TODO: enum
        self.video = kwargs.pop('video')

        player = kwargs.get('player')
        demon = kwargs.get('demon')

        if player is not None:
            self.player = EmbeddedPlayer(**player)
        else:
            self.player = None

        if demon is not None:
            self.demon = ShortDemon(**demon)
        else:
            self.demon = None


class ShortSubmitter(AutoRepr):
    def __init__(self, **kwargs):
        self.id = kwargs.pop('id')
        self.banned = kwargs.pop('banned')


class Submitter(ShortSubmitter):
    def __init__(self, etag, **kwargs):
        self.etag = etag
        self.records = [ShortRecord(**record)
                        for record in kwargs.pop('records')]

        super().__init__(**kwargs)


class Player(ShortPlayer):
    def __init__(self, etag, **kwargs):
        self.etag = etag
        self.created = [ShortDemon(**demon) for demon in kwargs.pop('created')]
        self.published = [ShortDemon(**demon)
                          for demon in kwargs.pop('published')]
        self.verified = [ShortDemon(**demon)
                         for demon in kwargs.pop('verified')]

        self.records = [ShortRecord(**record)
                        for record in kwargs.pop('records')]

        super().__init__(**kwargs)


class Demon(ShortDemon):
    def __init__(self, etag, **kwargs):
        self.etag = etag
        self.requirement = kwargs.pop('requirement')
        self.verifier = EmbeddedPlayer(**kwargs.pop('verifier'))
        self.creators = [EmbeddedPlayer(**creator)
                         for creator in kwargs.pop('creators')]
        self.records = [ShortRecord(**record)
                        for record in kwargs.pop('records')]

        publisher = EmbeddedPlayer(**kwargs.pop('publisher'))

        super().__init__(**kwargs, publisher=publisher)


class Record(ShortRecord):
    def __init__(self, etag, **kwargs):
        self.etag = etag
        self.submitter = kwargs.pop('submitter')

        super().__init__(**kwargs)
