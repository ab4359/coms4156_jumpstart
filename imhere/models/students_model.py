from model import Model
from datetime import datetime, date


class Students(Model):

    def __init__(self, sid):
        self.sid = sid

    def get_uni(self):
        query = 'select uni from students where sid = %s' % self.sid
        result = self.db.execute(query)
        return result.fetchone()[0]

    def get_courses(self):
        ds = self.get_client()
        query = ds.query(kind='enrolled_in')
        query.add_filter('sid', '=', self.sid)
        enrolledCourses = list(query.fetch())
        result = list()
        for enrolledCourse in enrolledCourses:
            query = ds.query(kind='courses')
            query.add_filter('cid', '=', enrolledCourse['cid'])
            result = result + list(query.fetch())

        return result

    def get_secret_and_seid(self):
        now = datetime.time(datetime.now())
        today = date.today()

        try:
            query = ('select secret, seid '
                     'from sessions, enrolled_in '
                     'where enrolled_in.sid = %s '
                     'and enrolled_in.cid = sessions.cid '
                     "and sessions.expires > '%s' "
                     "and sessions.day >= '%s'"
                     % (self.sid, now, today))
            result = self.db.execute(query)
            row = result.fetchone()
            secret = row[0]
            seid = row[1]
        except:
            secret, seid = None, -1

        return secret, seid

    def has_signed_in(self):
        _, seid = self.get_secret_and_seid()

        if seid == -1:
            return False
        else:

            query = ('select * from attendance_records, sessions '
                     'where attendance_records.seid = sessions.seid '
                     'and attendance_records.sid = %s '
                     'and sessions.seid = %s'
                     % (self.sid, seid))
            result = self.db.execute(query)
            return True if result.rowcount == 1 else False

    def insert_attendance_record(self, seid):
        query = 'insert into attendance_records values (%s, %s)' \
                % (self.sid, seid)
        self.db.execute(query)

    def get_num_attendance_records(self, cid):
        query = ('select * '
                 'from attendance_records, sessions '
                 'where attendance_records.seid = sessions.seid '
                 'and sessions.cid = %s '
                 'and attendance_records.sid = %s'
                 % (cid, self.sid))
        result = self.db.execute(query)
        return result.rowcount
