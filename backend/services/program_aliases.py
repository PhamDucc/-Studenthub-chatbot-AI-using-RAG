"""Expand common UET program abbreviations without adding student facts."""
import re

_NAMES = {
    'cntt': 'Công nghệ thông tin', 'khmt': 'Khoa học máy tính',
    'httt': 'Hệ thống thông tin', 'attt': 'An toàn thông tin',
    'ttnt': 'Trí tuệ nhân tạo', 'khdl': 'Khoa học dữ liệu',
    'ktmt': 'Kỹ thuật máy tính', 'vlkt': 'Vật lý kỹ thuật',
    'ktnl': 'Kỹ thuật năng lượng', 'ktđtvt': 'Kỹ thuật điện tử viễn thông',
    'ktdtvt': 'Kỹ thuật điện tử viễn thông',
    'mmt&ttdl': 'Mạng máy tính và truyền thông dữ liệu',
}
_ABBREVIATION = re.compile(r'\b(?:' + '|'.join(re.escape(name) for name in _NAMES) + r')\b', re.I)


def expand_program_names(text: str) -> str:
    return _ABBREVIATION.sub(lambda match: _NAMES[match.group().casefold()], text)
