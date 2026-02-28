from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone

from applications.poll.models import DailyPublication, InstagramTokenState, Vote
from applications.poll.publication import DailyCardGenerator, InstagramPublisher, InstagramTokenManager
from applications.poll.services import get_daily_poll_snapshot


class PollSnapshotTests(TestCase):
    def test_get_daily_poll_snapshot_with_votes(self):
        Vote.objects.create(option=Vote.OPTION_GOOD, session_key='a')
        Vote.objects.create(option=Vote.OPTION_GOOD, session_key='b')
        Vote.objects.create(option=Vote.OPTION_BAD, session_key='c')

        snapshot = get_daily_poll_snapshot()

        self.assertEqual(snapshot['title'], '¿Cómo vamos?')
        self.assertEqual(snapshot['good_count'], 2)
        self.assertEqual(snapshot['bad_count'], 1)
        self.assertEqual(snapshot['total'], 3)
        self.assertEqual(snapshot['good_pct_display'], 67)
        self.assertEqual(snapshot['bad_pct_display'], 33)


class DailyCardGeneratorTests(TestCase):
    @override_settings(MEDIA_ROOT='/tmp/cambiodemando_test_media')
    @patch('applications.poll.publication.render_to_string', return_value='<html></html>')
    @patch('applications.poll.publication.DailyCardGenerator._load_css', return_value='body{}')
    @patch('applications.poll.publication.DailyCardGenerator._capture_screenshot')
    @patch(
        'applications.poll.publication._get_daily_card_context',
        return_value={
            'title': '¿Cómo vamos?',
            'result_label': 'Dentro de todo bien',
            'good_count': 10,
            'bad_count': 2,
            'total': 12,
            'good_pct_display': 83,
            'bad_pct_display': 17,
            'good_dash': 417,
            'bad_dash': 85,
            'good_gap': 85,
            'bad_gap': 417,
            'circumference': 502,
            'offset_start': 0,
            'offset_red': 85,
            'card_image_data_uri': 'data:image/jpeg;base64,abc',
        },
    )
    def test_generate_creates_or_updates_daily_publication(
        self,
        _context_mock,
        _capture_mock,
        _load_css_mock,
        _render_mock,
    ):
        temp_media = Path('/tmp/cambiodemando_test_media')
        temp_media.mkdir(parents=True, exist_ok=True)

        publication_date = timezone.localdate()
        publication, out_path = DailyCardGenerator().generate(publication_date=publication_date, force=True)

        self.assertEqual(publication.publication_date, publication_date)
        self.assertEqual(publication.status, DailyPublication.STATUS_PUBLISH_PENDING)
        self.assertIn('daily-card-', out_path.name)
        self.assertTrue(publication.public_image_url.endswith(out_path.name + '/'))


class InstagramPublisherTests(TestCase):
    def test_publish_returns_same_when_already_published(self):
        publication = DailyPublication.objects.create(
            publication_date=timezone.localdate(),
            status=DailyPublication.STATUS_PUBLISHED,
            instagram_media_id='123',
        )

        result = InstagramPublisher().publish(publication)
        self.assertEqual(result.instagram_media_id, '123')

    @override_settings(INSTAGRAM_ACCESS_TOKEN='', INSTAGRAM_IG_USER_ID='')
    def test_publish_fails_without_credentials(self):
        publication = DailyPublication.objects.create(
            publication_date=timezone.localdate(),
            status=DailyPublication.STATUS_PUBLISH_PENDING,
            public_image_url='https://example.com/daily-card-2026-02-27.jpg',
        )
        with self.assertRaises(RuntimeError):
            InstagramPublisher().publish(publication)


class InstagramTokenManagerTests(TestCase):
    @override_settings(
        INSTAGRAM_ACCESS_TOKEN='env-token',
        INSTAGRAM_APP_ID='123',
        INSTAGRAM_APP_SECRET='abc',
        INSTAGRAM_REFRESH_MODE='facebook_exchange',
    )
    @patch('applications.poll.publication.InstagramTokenManager._http_get_json')
    def test_refresh_token_updates_state(self, http_get_json_mock):
        http_get_json_mock.return_value = {'access_token': 'new-token', 'expires_in': 3600}
        manager = InstagramTokenManager()

        token, _expires_at = manager.refresh_token()

        self.assertEqual(token, 'new-token')
        state = InstagramTokenState.objects.first()
        self.assertIsNotNone(state)
        self.assertEqual(state.access_token, 'new-token')

    @override_settings(
        INSTAGRAM_ACCESS_TOKEN='env-token',
        INSTAGRAM_APP_ID='123',
        INSTAGRAM_APP_SECRET='abc',
        INSTAGRAM_REFRESH_THRESHOLD_DAYS=7,
    )
    @patch('applications.poll.publication.InstagramTokenManager.refresh_token')
    def test_refresh_if_needed_when_expiring_soon(self, refresh_token_mock):
        refresh_token_mock.return_value = ('refreshed', timezone.now())
        InstagramTokenState.objects.create(
            access_token='stored-token',
            expires_at=timezone.now() + timedelta(days=2),
        )
        manager = InstagramTokenManager()

        manager.refresh_if_needed()

        refresh_token_mock.assert_called_once()
