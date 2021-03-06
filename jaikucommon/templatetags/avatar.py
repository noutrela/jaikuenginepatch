# Copyright 2009 Google Inc.
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

from django import template
from django.template.defaultfilters import stringfilter
from django.utils import http

from jaikucommon.util import create_nonce, safe
from jaikucommon import api
from jaikucommon import exception
import settings

def safe_avatar(f):
  def _wrapper(*args, **kwargs):
    try:
      return f(*args, **kwargs)
    except:
      exception.log_exception()
      if settings.DEBUG:
        return 'FAIL'
      else:
        return ''
  return _wrapper

register = template.Library()

@register.filter(name="avatar")
@safe
@safe_avatar
def avatar(value, arg="t"):
  size = arg
  dimensions = api.AVATAR_IMAGE_SIZES[size]
  # TODO shard these
  # TODO cache these
  path = avatar_url(value, arg)

  return '<img src="%s" class="photo" alt="%s" width="%s" height="%s" />' % (
      path, value.display_nick(), dimensions[0], dimensions[1])

# noncached_avatar arguments: size (mandatory), tag id (optional)
# Usage: {{view|noncached_avatar:"f,current"}}
@register.filter(name="noncached_avatar")
@safe
@safe_avatar
def noncached_avatar(value, args):
  parts = args.split(",")
  size = parts[0]
  dimensions = api.AVATAR_IMAGE_SIZES[size]
  tag_id = ""
  if len(parts) > 1:
    tag_id = 'id="%s"' % (parts[1])

  path = avatar_url(value, size)
  nonce = create_nonce(value, "avatar_preview")
  nick = value.display_nick()
  return '<img src="%s?%s" class="photo" alt="%s" width="%s" height="%s" %s/>' % (
      path, nonce, nick, dimensions[0], dimensions[1], tag_id)

@register.filter(name="avatar_url")
@safe
@safe_avatar
def avatar_url(value, arg="t"):
  size = arg
  icon = value.extra.get('icon', 'avatar_default')

  # TODO shard these
  # TODO cache these
  path = "%s_%s.jpg" % (icon, size)
  if icon.find("default") >= 0:
    return '%sglobal/image/%s' % (settings.MEDIA_URL, http.urlquote(path))
  return '/image/%s' % (http.urlquote(path))

@register.filter(name="linked_avatar")
@safe
@safe_avatar
def linked_avatar(value, args):
  parts = args.split(",")
  arg = parts[0]
  rel = len(parts) > 1 and parts[1] or None

  if rel:
    rel_attr = ' rel="%s"' % rel
  else:
    rel_attr = ''

  return ('<a class="url" href="%s"%s>%s</a>' % 
      (value.url(), rel_attr, avatar(value, arg)))
