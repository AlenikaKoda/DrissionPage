# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Website  : https://DrissionPage.cn
@Copyright: (c) 2020 by g1879, Inc. All Rights Reserved.
"""
from .locator import is_str_loc, is_selenium_loc
from .._elements.none_element import NoneElement
from .._functions.settings import Settings as _S
from .._functions.tools import wait_until
from ..errors import LocatorError


class SessionElementsList(list):
    def __init__(self, owner=None, *args):
        super().__init__(*args)
        self._owner = owner

    def __getitem__(self, item):
        cls = type(self)
        if isinstance(item, slice):
            return cls(self._owner, super().__getitem__(item))
        elif isinstance(item, int):
            return super().__getitem__(item)
        else:
            raise ValueError(_S._lang.joinn(_S._lang.INDEX_FORMAT, CURR_VAL=item))

    @property
    def vals(self):
        return Getter(self)

    @property
    def filter(self):
        return SessionFilter(self)

    @property
    def filter_one(self):
        return SessionFilterOne(self)


class ChromiumElementsList(SessionElementsList):

    @property
    def filter(self):
        return ChromiumFilter(self)

    @property
    def filter_one(self):
        return ChromiumFilterOne(self)


class SessionFilterOne(object):
    def __init__(self, _list):
        self._list = _list

    def __call__(self, tag=..., contain_text=..., text_is=..., equal=True, index=1, **kwargs):
        return self.any_of(tag=tag, contain_text=contain_text, text_is=text_is, equal=equal, index=index, **kwargs)

    def any_of(self, tag=..., contain_text=..., text_is=..., equal=True, index=1, **kwargs):
        return any_of_s(self._list, tag=tag, contain_text=contain_text, text_is=text_is, equal=equal, index=index,
                        **kwargs)

    def tag(self, name, equal=True, index=1):
        num = 0
        name = name.lower()
        if equal:
            for i in self._list:
                if not isinstance(i, str) and i.tag == name:
                    num += 1
                    if index == num:
                        return i
        else:
            for i in self._list:
                if not isinstance(i, str) and i.tag != name:
                    num += 1
                    if index == num:
                        return i
        return NoneElement(self._list._owner, 'filter.tag()', args={'name': name, 'equal': equal, 'index': index})

    def text(self, text, fuzzy=True, contain=True, index=1):
        num = 0
        if contain:
            for i in self._list:
                t = i if isinstance(i, str) else i.raw_text
                if (fuzzy and text in t) or (not fuzzy and text == t):
                    num += 1
                    if index == num:
                        return i
        else:
            for i in self._list:
                t = i if isinstance(i, str) else i.raw_text
                if (fuzzy and text not in t) or (not fuzzy and text != t):
                    num += 1
                    if index == num:
                        return i
        return NoneElement(self._list._owner, 'filter.text()',
                           args={'text': text, 'fuzzy': fuzzy, 'contain': contain, 'index': index})

    def attr(self, name, value, equal=True, index=1):
        return self._get_attr(name, value, 'attr', equal=equal, index=index)

    def _get_attr(self, name, value, method, equal=True, index=1):
        num = 0
        if equal:
            for i in self._list:
                if not isinstance(i, str) and getattr(i, method)(name) == value:
                    num += 1
                    if index == num:
                        return i
        else:
            for i in self._list:
                if not isinstance(i, str) and getattr(i, method)(name) != value:
                    num += 1
                    if index == num:
                        return i
        return NoneElement(self._list._owner, f'filter.{method}()',
                           args={'name': name, 'value': value, 'equal': equal, 'index': index})


class SessionFilter(object):
    _LIST_CLASS = SessionElementsList

    def __init__(self, _list):
        self._list = _list

    def __iter__(self):
        return iter(self._list)

    def __next__(self):
        return next(self._list)

    def __len__(self):
        return len(self._list)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return SessionFilter(self._list[item.start: item.stop: item.step])
        elif isinstance(item, int):
            return self._list[item]
        else:
            raise ValueError(_S._lang.joinn(_S._lang.INDEX_FORMAT, CURR_VAL=item))

    def __repr__(self):
        return str(self._list)

    def __call__(self, tag=..., contain_text=..., text_is=..., equal=True, index=..., **kwargs):
        return self.any_of(tag=tag, contain_text=contain_text, text_is=text_is, equal=equal, **kwargs)

    def any_of(self, tag=..., contain_text=..., text_is=..., equal=True, index=..., **kwargs):
        return any_of_s(self._list, tag=tag, contain_text=contain_text, text_is=text_is, equal=equal, **kwargs)

    @property
    def vals(self):
        return self._list.vals

    def tag(self, name, equal=True):
        self._list = _tag_all(self._list, self._LIST_CLASS(owner=self._list._owner), name=name, equal=equal)
        return self

    def attr(self, name, value, equal=True):
        self._list = _attr_all(self._list, self._LIST_CLASS(owner=self._list._owner),
                               name=name, value=value, method='attr', equal=equal)
        return self

    def text(self, text, fuzzy=True, contain=True):
        self._list = _text_all(self._list, self._LIST_CLASS(owner=self._list._owner),
                               text=text, fuzzy=fuzzy, contain=contain)
        return self


class ChromiumFilterOne(SessionFilterOne):

    def displayed(self, equal=True, index=1):
        return self._any_state('is_displayed', equal=equal, index=index)

    def checked(self, equal=True, index=1):
        return self._any_state('is_checked', equal=equal, index=index)

    def selected(self, equal=True, index=1):
        return self._any_state('is_selected', equal=equal, index=index)

    def enabled(self, equal=True, index=1):
        return self._any_state('is_enabled', equal=equal, index=index)

    def clickable(self, equal=True, index=1):
        return self._any_state('is_clickable', equal=equal, index=index)

    def have_rect(self, equal=True, index=1):
        return self._any_state('has_rect', equal=equal, index=index)

    def style(self, name, value, equal=True, index=1):
        return self._get_attr(name, value, 'style', equal=equal, index=index)

    def property(self, name, value, equal=True, index=1):
        return self._get_attr(name, value, 'property', equal=equal, index=index)

    def _any_state(self, name, equal=True, index=1):
        num = 0
        if equal:
            for i in self._list:
                if not isinstance(i, str) and getattr(i.states, name):
                    num += 1
                    if index == num:
                        return i
        else:
            for i in self._list:
                if not isinstance(i, str) and not getattr(i.states, name):
                    num += 1
                    if index == num:
                        return i
        return NoneElement(self._list._owner, f'{name}()', args={'equal': equal, 'index': index})

    def any_of(self, tag=..., contain_text=..., text_is=..., displayed=..., checked=..., selected=..., enabled=...,
               clickable=..., have_rect=..., equal=True, index=1, **kwargs):
        return any_of_c(self._list, tag=tag, contain_text=contain_text, text_is=text_is, displayed=displayed,
                        checked=checked, selected=selected, enabled=enabled, clickable=clickable, have_rect=have_rect,
                        equal=equal, index=index, **kwargs)


class ChromiumFilter(SessionFilter):
    _LIST_CLASS = ChromiumElementsList

    def __getitem__(self, item):
        if isinstance(item, slice):
            return ChromiumFilter(self._list[item.start: item.stop: item.step])
        elif isinstance(item, int):
            return self._list[item]
        else:
            raise ValueError(_S._lang.joinn(_S._lang.INDEX_FORMAT, CURR_VAL=item))

    def __call__(self, tag=..., contain_text=..., text_is=..., displayed=None, checked=None, selected=None,
                 enabled=None, clickable=None, have_rect=None, equal=True, index=..., **kwargs):
        return any_of_c(self._list, tag=tag, contain_text=contain_text, text_is=text_is, displayed=displayed,
                        checked=checked, selected=selected, enabled=enabled, clickable=clickable, have_rect=have_rect,
                        equal=equal, index=index, **kwargs)

    def any_of(self, tag=..., contain_text=..., text_is=..., displayed=None, checked=None, selected=None, enabled=None,
               clickable=None, have_rect=None, equal=True, index=..., **kwargs):
        return any_of_c(self._list, tag=tag, contain_text=contain_text, text_is=text_is, displayed=displayed,
                        checked=checked, selected=selected, enabled=enabled, clickable=clickable, have_rect=have_rect,
                        equal=equal, index=index, **kwargs)

    def displayed(self, equal=True):
        return self._any_state('is_displayed', equal=equal)

    def checked(self, equal=True):
        return self._any_state('is_checked', equal=equal)

    def selected(self, equal=True):
        return self._any_state('is_selected', equal=equal)

    def enabled(self, equal=True):
        return self._any_state('is_enabled', equal=equal)

    def clickable(self, equal=True):
        return self._any_state('is_clickable', equal=equal)

    def have_rect(self, equal=True):
        return self._any_state('has_rect', equal=equal)

    def style(self, name, value, equal=True):
        return self._get_attr(name, value, 'style', equal=equal)

    def property(self, name, value, equal=True):
        return self._get_attr(name, value, 'property', equal=equal)

    def _any_state(self, name, equal=True):
        r = ChromiumElementsList(owner=self._list._owner)
        if equal:
            for i in self._list:
                if not isinstance(i, str) and getattr(i.states, name):
                    r.append(i)
        else:
            for i in self._list:
                if not isinstance(i, str) and not getattr(i.states, name):
                    r.append(i)
        self._list = r
        return self


class Getter(object):
    def __init__(self, _list):
        self._list = _list

    def links(self):
        return [e.link for e in self._list if not isinstance(e, str)]

    def texts(self):
        texts = []
        for t in self._list:
            if hasattr(t, 'text'):
                texts.append(t.text)
            elif isinstance(t, str):
                texts.append(t)
        return texts

    def attrs(self, name):
        return [e.attr(name) for e in self._list if not isinstance(e, str)]


def get_eles(locators, owner, any_one=False, first_ele=True, timeout=10):
    def do():
        for loc in locators:
            if res[loc]:
                continue
            ele = owner._ele(loc, timeout=0, raise_err=False, index=1 if first_ele else None, method='find()')
            res[loc] = ele
            if ele and any_one:
                return True
        return True if all(res.values()) else None

    if is_selenium_loc(locators):
        locators = (locators,)
    res = {loc: None for loc in locators}
    wait_until(do, timeout=timeout)
    return res


def get_frame(owner, loc_ind_ele, timeout=None):
    if isinstance(loc_ind_ele, str):
        if is_str_loc(loc_ind_ele):
            xpath = loc_ind_ele
        else:
            xpath = f'xpath://*[(name()="iframe" or name()="frame") and (@name="{loc_ind_ele}" or @id="{loc_ind_ele}")]'
        ele = owner._ele(xpath, timeout=timeout)
        if ele and ele._type != 'ChromiumFrame':
            raise LocatorError(_S._lang.LOC_NOT_FOR_FRAME, LOCATOR=loc_ind_ele)
        r = ele

    elif isinstance(loc_ind_ele, tuple):
        ele = owner._ele(loc_ind_ele, timeout=timeout)
        if ele and ele._type != 'ChromiumFrame':
            raise LocatorError(_S._lang.LOC_NOT_FOR_FRAME, LOCATOR=loc_ind_ele)
        r = ele

    elif isinstance(loc_ind_ele, int):
        ele = owner._ele('@|tag():iframe@|tag():frame', timeout=timeout, index=loc_ind_ele)
        if ele and ele._type != 'ChromiumFrame':
            raise LocatorError(_S._lang.LOC_NOT_FOR_FRAME, LOCATOR=loc_ind_ele)
        r = ele

    elif getattr(loc_ind_ele, '_type', None) == 'ChromiumFrame':
        r = loc_ind_ele

    else:
        raise ValueError(_S._lang.joinn(_S._lang.INCORRECT_VAL_, 'loc_ind_ele',
                                        ALLOW_VAL=_S._lang.FRAME_LOC_FORMAT, CURR_VAL=loc_ind_ele))

    if isinstance(r, NoneElement):
        r.method = 'get_frame()'
        r.args = {'loc_ind_ele': loc_ind_ele}
    return r


def _attr_all(src_list, aim_list, name, value, method, equal=True):
    if equal:
        for i in src_list:
            if not isinstance(i, str) and getattr(i, method)(name) == value:
                aim_list.append(i)
    else:
        for i in src_list:
            if not isinstance(i, str) and getattr(i, method)(name) != value:
                aim_list.append(i)
    return aim_list


def _tag_all(src_list, aim_list, name, equal=True):
    name = name.lower()
    if equal:
        for i in src_list:
            if not isinstance(i, str) and i.tag == name:
                aim_list.append(i)
    else:
        for i in src_list:
            if not isinstance(i, str) and i.tag != name:
                aim_list.append(i)
    return aim_list


def _text_all(src_list, aim_list, text, fuzzy=True, contain=True):
    """以是否含有指定文本为条件筛选元素
    :param text: 用于匹配的文本
    :param fuzzy: 是否模糊匹配
    :param contain: 是否包含该字符串，False表示不包含
    :return: 筛选结果
    """
    if contain:
        for i in src_list:
            t = i if isinstance(i, str) else i.raw_text
            if (fuzzy and text in t) or (not fuzzy and text == t):
                aim_list.append(i)
    else:
        for i in src_list:
            t = i if isinstance(i, str) else i.raw_text
            if (fuzzy and text not in t) or (not fuzzy and text != t):
                aim_list.append(i)
    return aim_list


def any_of_s(_list, tag=..., contain_text=..., text_is=..., equal=True, index=..., **kwargs):
    if isinstance(index, int):
        if index == 0:
            index = 1
        elif index < 0:
            _list = _list[::-1]
            index = abs(index)
        num = 0
        if equal:
            for i in _list:
                if isinstance(i, str):
                    continue
                if ((tag is not Ellipsis and i.tag == tag.lower())
                        or (contain_text is not Ellipsis and i.text and contain_text in i.text)
                        or (text_is is not Ellipsis and text_is == i.text)):
                    num += 1
                else:
                    for attr, val in kwargs.items():
                        if i.attrs.get(attr) == val:
                            num += 1
                            break
                if num == index:
                    return i
        else:
            for i in _list:
                if isinstance(i, str):
                    continue
                if ((tag is not Ellipsis and i.tag != tag.lower())
                        or (contain_text is not Ellipsis and (not i.text or contain_text not in i.text))
                        or (text_is is not Ellipsis and text_is != i.text)):
                    num += 1
                else:
                    for attr, val in kwargs.items():
                        if i.attrs.get(attr) != val:
                            num += 1
                            break
                if num == index:
                    return i

        return NoneElement(_list._owner, method='filter.any_of()', args={'tag': tag, 'contain_text': contain_text,
                                                                         'text_is': text_is, 'equal': equal,
                                                                         'index': index, **kwargs})
    r = SessionElementsList(owner=_list._owner)
    if equal:
        for i in _list:
            if isinstance(i, str):
                continue
            if ((tag is not Ellipsis and i.tag == tag.lower())
                    or (contain_text is not Ellipsis and i.text and contain_text in i.text)
                    or (text_is is not Ellipsis and text_is == i.text)):
                r.append(i)
            else:
                for attr, val in kwargs.items():
                    if i.attrs.get(attr) == val:
                        r.append(i)
                        break
    else:
        for i in _list:
            if isinstance(i, str):
                continue
            if ((tag is not Ellipsis and i.tag != tag.lower())
                    or (contain_text is not Ellipsis and (not i.text or contain_text not in i.text))
                    or (text_is is not Ellipsis and text_is != i.text)):
                r.append(i)
            else:
                for attr, val in kwargs.items():
                    if i.attrs.get(attr) != val:
                        r.append(i)
                        break
    return SessionFilter(r)


def any_of_c(_list, tag=..., contain_text=..., text_is=..., displayed=..., checked=..., selected=..., enabled=...,
             clickable=..., have_rect=..., equal=True, index=..., **kwargs):
    if isinstance(index, int):
        if index == 0:
            index = 1
        elif index < 0:
            _list = _list[::-1]
            index = abs(index)
        num = 0
        if equal:
            for i in _list:
                if isinstance(i, str):
                    continue
                if ((tag is not Ellipsis and i.tag == tag.lower())
                        or (contain_text is not Ellipsis and i.text and contain_text in i.text)
                        or (text_is is not Ellipsis and text_is == i.text)
                        or (displayed is not Ellipsis and (displayed is True and i.states.is_displayed)
                            or (displayed is False and not i.states.is_displayed))
                        or (checked is not Ellipsis and (checked is True and i.states.is_checked)
                            or (checked is False and not i.states.is_checked))
                        or (selected is not Ellipsis and (selected is True and i.states.is_selected)
                            or (selected is False and not i.states.is_selected))
                        or (enabled is not Ellipsis and (enabled is True and i.states.is_enabled)
                            or (enabled is False and not i.states.is_enabled))
                        or (clickable is not Ellipsis and (clickable is True and i.states.is_clickable)
                            or (clickable is False and not i.states.is_clickable))
                        or (have_rect is not Ellipsis and (have_rect is True and i.states.has_rect)
                            or (have_rect is False and not i.states.has_rect))):
                    num += 1
                else:
                    for attr, val in kwargs.items():
                        if i.attrs.get(attr) == val:
                            num += 1
                            break
                if num == index:
                    return i
        else:
            for i in _list:
                if isinstance(i, str):
                    continue
                if ((tag is not Ellipsis and i.tag != tag.lower())
                        or (contain_text is not Ellipsis and (not i.text or contain_text not in i.text))
                        or (text_is is not Ellipsis and text_is != i.text)
                        or (displayed is not Ellipsis and (displayed is False and i.states.is_displayed)
                            or (displayed is True and not i.states.is_displayed))
                        or (checked is not Ellipsis and (checked is False and i.states.is_checked)
                            or (checked is True and not i.states.is_checked))
                        or (selected is not Ellipsis and (selected is False and i.states.is_selected)
                            or (selected is True and not i.states.is_selected))
                        or (enabled is not Ellipsis and (enabled is False and i.states.is_enabled)
                            or (enabled is True and not i.states.is_enabled))
                        or (clickable is not Ellipsis and (clickable is False and i.states.is_clickable)
                            or (clickable is True and not i.states.is_clickable))
                        or (have_rect is not Ellipsis and (have_rect is False and i.states.has_rect)
                            or (have_rect is True and not i.states.has_rect))):
                    num += 1
                else:
                    for attr, val in kwargs.items():
                        if i.attrs.get(attr) != val:
                            num += 1
                            break
                if num == index:
                    return i

        return NoneElement(_list._owner, method='filter.any_of()', args={'tag': tag, 'contain_text': contain_text,
                                                                         'text_is': text_is, 'equal': equal,
                                                                         'index': index, **kwargs})

    r = ChromiumElementsList(owner=_list._owner)
    if equal:
        for i in _list:
            if isinstance(i, str):
                continue
            if ((tag is not Ellipsis and i.tag == tag.lower())
                    or (contain_text is not Ellipsis and i.text and contain_text in i.text)
                    or (text_is is not Ellipsis and text_is == i.text)
                    or (displayed is not Ellipsis and (displayed is True and i.states.is_displayed)
                        or (displayed is False and not i.states.is_displayed))
                    or (checked is not Ellipsis and (checked is True and i.states.is_checked)
                        or (checked is False and not i.states.is_checked))
                    or (selected is not Ellipsis and (selected is True and i.states.is_selected)
                        or (selected is False and not i.states.is_selected))
                    or (enabled is not Ellipsis and (enabled is True and i.states.is_enabled)
                        or (enabled is False and not i.states.is_enabled))
                    or (clickable is not Ellipsis and (clickable is True and i.states.is_clickable)
                        or (clickable is False and not i.states.is_clickable))
                    or (have_rect is not Ellipsis and (have_rect is True and i.states.has_rect)
                        or (have_rect is False and not i.states.has_rect))):
                r.append(i)
            else:
                for attr, val in kwargs.items():
                    if i.attrs.get(attr) == val:
                        r.append(i)
                        break
    else:
        for i in _list:
            if isinstance(i, str):
                continue
            if ((tag is not Ellipsis and i.tag != tag.lower())
                    or (contain_text is not Ellipsis and (not i.text or contain_text not in i.text))
                    or (text_is is not Ellipsis and text_is != i.text)
                    or (displayed is not Ellipsis and (displayed is False and i.states.is_displayed)
                        or (displayed is True and not i.states.is_displayed))
                    or (checked is not Ellipsis and (checked is False and i.states.is_checked)
                        or (checked is True and not i.states.is_checked))
                    or (selected is not Ellipsis and (selected is False and i.states.is_selected)
                        or (selected is True and not i.states.is_selected))
                    or (enabled is not Ellipsis and (enabled is False and i.states.is_enabled)
                        or (enabled is True and not i.states.is_enabled))
                    or (clickable is not Ellipsis and (clickable is False and i.states.is_clickable)
                        or (clickable is True and not i.states.is_clickable))
                    or (have_rect is not Ellipsis and (have_rect is False and i.states.has_rect)
                        or (have_rect is True and not i.states.has_rect))):
                r.append(i)
            else:
                for attr, val in kwargs.items():
                    if i.attrs.get(attr) != val:
                        r.append(i)
                        break
    return ChromiumFilter(r)
