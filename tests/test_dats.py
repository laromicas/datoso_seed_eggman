"""TeknoParrot folders get a date and version, so unchanged ones are skipped and re-releases are not."""

from datoso_seed_eggman.dats import TeknoparrotDat, header_field

DAT = '<?xml version="1.0"?>\n<datafile>\n<header><name>{name}</name><date>{date}</date><version></version></header>\n</datafile>\n'


def folder_with(tmp_path, name, date, extra=''):
    folder = tmp_path / name
    folder.mkdir()
    (folder / f'{name} ({date}_RomVault).dat').write_text(DAT.format(name=name, date=date) + extra, encoding='utf-8')
    return folder


def test_date_from_header_and_size_as_version(tmp_path):
    folder = folder_with(tmp_path, 'TeknoParrot Collection', '2026-11-23')
    dat = TeknoparrotDat(file=folder)
    size = next(folder.glob('*.dat')).stat().st_size
    assert (dat.get_date(), dat.get_version()) == ('2026-11-23', str(size))


def test_same_date_rerelease_gets_a_new_version(tmp_path):
    (tmp_path / 'first').mkdir()
    (tmp_path / 'fixed').mkdir()
    first = folder_with(tmp_path / 'first', 'TeknoParrot Collection', '2026-09-05')
    fixed = folder_with(tmp_path / 'fixed', 'TeknoParrot Collection', '2026-09-05', '<!-- fixed -->')
    assert TeknoparrotDat(file=first).get_version() != TeknoparrotDat(file=fixed).get_version()


def test_header_field(tmp_path):
    dat = next(folder_with(tmp_path, 'X', '2026-01-02').glob('*.dat'))
    assert (header_field(dat, 'date'), header_field(dat, 'version'), header_field(dat, 'author')) == \
        ('2026-01-02', None, None)
