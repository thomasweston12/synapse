# Copyright 2014-2016 OpenMarket Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from synapse.api.errors import SynapseError
from synapse.types import MXCUri, RoomAlias, UserID, map_username_to_mxid_localpart

from tests import unittest


class UserIDTestCase(unittest.HomeserverTestCase):
    def test_parse(self):
        user = UserID.from_string("@1234abcd:test")

        self.assertEqual("1234abcd", user.localpart)
        self.assertEqual("test", user.domain)
        self.assertEqual(True, self.hs.is_mine(user))

    def test_parse_rejects_empty_id(self):
        with self.assertRaises(SynapseError):
            UserID.from_string("")

    def test_parse_rejects_missing_sigil(self):
        with self.assertRaises(SynapseError):
            UserID.from_string("alice:example.com")

    def test_parse_rejects_missing_separator(self):
        with self.assertRaises(SynapseError):
            UserID.from_string("@alice.example.com")

    def test_validation_rejects_missing_domain(self):
        self.assertFalse(UserID.is_valid("@alice:"))

    def test_build(self):
        user = UserID("5678efgh", "my.domain")

        self.assertEqual(user.to_string(), "@5678efgh:my.domain")

    def test_compare(self):
        userA = UserID.from_string("@userA:my.domain")
        userAagain = UserID.from_string("@userA:my.domain")
        userB = UserID.from_string("@userB:my.domain")

        self.assertTrue(userA == userAagain)
        self.assertTrue(userA != userB)


class RoomAliasTestCase(unittest.HomeserverTestCase):
    def test_parse(self):
        room = RoomAlias.from_string("#channel:test")

        self.assertEqual("channel", room.localpart)
        self.assertEqual("test", room.domain)
        self.assertEqual(True, self.hs.is_mine(room))

    def test_build(self):
        room = RoomAlias("channel", "my.domain")

        self.assertEqual(room.to_string(), "#channel:my.domain")

    def test_validate(self):
        id_string = "#test:domain,test"
        self.assertFalse(RoomAlias.is_valid(id_string))


class MapUsernameTestCase(unittest.TestCase):
    def testPassThrough(self):
        self.assertEqual(map_username_to_mxid_localpart("test1234"), "test1234")

    def testUpperCase(self):
        self.assertEqual(map_username_to_mxid_localpart("tEST_1234"), "test_1234")
        self.assertEqual(
            map_username_to_mxid_localpart("tEST_1234", case_sensitive=True),
            "t_e_s_t__1234",
        )

    def testSymbols(self):
        self.assertEqual(
            map_username_to_mxid_localpart("test=$?_1234"), "test=3d=24=3f_1234"
        )

    def testLeadingUnderscore(self):
        self.assertEqual(map_username_to_mxid_localpart("_test_1234"), "=5ftest_1234")

    def testNonAscii(self):
        # this should work with either a unicode or a bytes
        self.assertEqual(map_username_to_mxid_localpart("têst"), "t=c3=aast")
        self.assertEqual(map_username_to_mxid_localpart("têst".encode()), "t=c3=aast")


class MXCUriTestCase(unittest.TestCase):
    def test_valid_mxc_uris(self):
        """Tests that a series of valid mxc uris are parsed correctly."""
        # Converting an MXCUri to its str representation
        mxc_1 = MXCUri(server_name="example.com", media_id="84n8493hnfsjkbcu")
        self.assertEqual(mxc_1.to_string(), "mxc://example.com/84n8493hnfsjkbcu")

        mxc_2 = MXCUri(
            server_name="192.168.1.17:8008", media_id="bajkad89h31ausdhoqqasd"
        )
        self.assertEqual(
            mxc_2.to_string(), "mxc://192.168.1.17:8008/bajkad89h31ausdhoqqasd"
        )

        mxc_3 = MXCUri(server_name="123.123.123.123", media_id="000000000000")
        self.assertEqual(mxc_3.to_string(), "mxc://123.123.123.123/000000000000")

        # Converting a str to its MXCUri representation
        mxcuri_1 = MXCUri.from_str("mxc://example.com/g12789g890ajksjk")
        self.assertEqual(mxcuri_1.server_name, "example.com")
        self.assertEqual(mxcuri_1.media_id, "g12789g890ajksjk")

        mxcuri_2 = MXCUri.from_str("mxc://localhost:8448/abcdefghijklmnopqrstuvwxyz")
        self.assertEqual(mxcuri_2.server_name, "localhost:8448")
        self.assertEqual(mxcuri_2.media_id, "abcdefghijklmnopqrstuvwxyz")

        mxcuri_3 = MXCUri.from_str("mxc://[::1]/abcdefghijklmnopqrstuvwxyz")
        self.assertEqual(mxcuri_3.server_name, "[::1]")
        self.assertEqual(mxcuri_3.media_id, "abcdefghijklmnopqrstuvwxyz")

        mxcuri_4 = MXCUri.from_str("mxc://123.123.123.123:32112/12893y81283781023")
        self.assertEqual(mxcuri_4.server_name, "123.123.123.123:32112")
        self.assertEqual(mxcuri_4.media_id, "12893y81283781023")

        mxcuri_5 = MXCUri.from_str("mxc://domain/abcdefg")
        self.assertEqual(mxcuri_5.server_name, "domain")
        self.assertEqual(mxcuri_5.media_id, "abcdefg")

    def test_invalid_mxc_uris(self):
        """Tests that a series of invalid mxc uris are appropriately rejected."""
        # Converting a str to its MXCUri representation
        with self.assertRaises(ValueError):
            MXCUri.from_str("http://example.com/abcdef")

        with self.assertRaises(ValueError):
            MXCUri.from_str("mxc:///example.com/abcdef")

        with self.assertRaises(ValueError):
            MXCUri.from_str("mxc://example.com//abcdef")

        with self.assertRaises(ValueError):
            MXCUri.from_str("mxc://example.com/abcdef/")

        with self.assertRaises(ValueError):
            MXCUri.from_str("mxc://example.com/abc/abcdef")

        with self.assertRaises(ValueError):
            MXCUri.from_str("mxc://example.com/abc/abcdef")

        with self.assertRaises(ValueError):
            MXCUri.from_str("mxc:///abcdef")

        with self.assertRaises(ValueError):
            MXCUri.from_str("mxc://example.com")

        with self.assertRaises(ValueError):
            MXCUri.from_str("mxc://example.com/")

        with self.assertRaises(ValueError):
            MXCUri.from_str("mxc:///")

        with self.assertRaises(ValueError):
            MXCUri.from_str("")

        with self.assertRaises(ValueError):
            MXCUri.from_str(None)  # type: ignore
