# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'PerfectTeam.player_1_description'
        db.add_column('registration_perfectteam', 'player_1_description', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True), keep_default=False)

        # Adding field 'PerfectTeam.player_2_description'
        db.add_column('registration_perfectteam', 'player_2_description', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True), keep_default=False)

        # Adding field 'PerfectTeam.player_3_description'
        db.add_column('registration_perfectteam', 'player_3_description', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True), keep_default=False)

        # Adding field 'PerfectTeam.player_4_description'
        db.add_column('registration_perfectteam', 'player_4_description', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'PerfectTeam.player_1_description'
        db.delete_column('registration_perfectteam', 'player_1_description')

        # Deleting field 'PerfectTeam.player_2_description'
        db.delete_column('registration_perfectteam', 'player_2_description')

        # Deleting field 'PerfectTeam.player_3_description'
        db.delete_column('registration_perfectteam', 'player_3_description')

        # Deleting field 'PerfectTeam.player_4_description'
        db.delete_column('registration_perfectteam', 'player_4_description')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'foundry.country': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Country'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minimum_age': ('django.db.models.fields.PositiveIntegerField', [], {'default': '18'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '32', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'foundry.member': {
            'Meta': {'object_name': 'Member', '_ormbases': ['auth.User']},
            'about_me': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['foundry.Country']", 'null': 'True', 'blank': 'True'}),
            'crop_from': ('django.db.models.fields.CharField', [], {'default': "'center'", 'max_length': '10', 'blank': 'True'}),
            'date_taken': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'effect': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'member_related'", 'null': 'True', 'to': "orm['photologue.PhotoEffect']"}),
            'facebook_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'mobile_number': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'receive_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'receive_sms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'twitter_username': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'view_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'friends.memberfriend': {
            'Meta': {'object_name': 'MemberFriend'},
            'friend': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'member_friend_friend'", 'to': "orm['foundry.Member']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'member_friend_member'", 'to': "orm['foundry.Member']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'invited'", 'max_length': '32', 'db_index': 'True'})
        },
        'photologue.photoeffect': {
            'Meta': {'object_name': 'PhotoEffect'},
            'background_color': ('django.db.models.fields.CharField', [], {'default': "'#FFFFFF'", 'max_length': '7'}),
            'brightness': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'color': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'contrast': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'filters': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'reflection_size': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'reflection_strength': ('django.db.models.fields.FloatField', [], {'default': '0.59999999999999998'}),
            'sharpness': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'transpose_method': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'})
        },
        'registration.offsiteinvite': {
            'Meta': {'object_name': 'OffSiteInvite'},
            'accepted_member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['foundry.Member']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invitations_sent'", 'to': "orm['foundry.Member']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member_friendship': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['friends.MemberFriend']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'invited'", 'max_length': '16'}),
            'to_friend_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'to_mobile_number': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'url_token': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registration.URLToken']"})
        },
        'registration.perfectteam': {
            'Meta': {'object_name': 'PerfectTeam'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player_1': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'player_1_description': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'player_2': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'player_2_description': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'player_3': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'player_3_description': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'player_4': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'player_4_description': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'team_name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'registration.perfectteamentry': {
            'Meta': {'object_name': 'PerfectTeamEntry'},
            'friend_1_invite': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'perfect_team_friend_1'", 'null': 'True', 'to': "orm['registration.OffSiteInvite']"}),
            'friend_1_mobile_number': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'friend_1_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'friend_2_invite': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'perfect_team_friend_2'", 'null': 'True', 'to': "orm['registration.OffSiteInvite']"}),
            'friend_2_mobile_number': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'friend_2_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'friend_3_invite': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'perfect_team_friend_3'", 'null': 'True', 'to': "orm['registration.OffSiteInvite']"}),
            'friend_3_mobile_number': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'friend_3_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'friend_4_invite': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'perfect_team_friend_4'", 'null': 'True', 'to': "orm['registration.OffSiteInvite']"}),
            'friend_4_mobile_number': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'friend_4_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'from_member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['foundry.Member']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['registration.PerfectTeam']"})
        },
        'registration.urltoken': {
            'Meta': {'object_name': 'URLToken'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tiny_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['registration']
