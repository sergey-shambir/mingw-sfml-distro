from __future__ import print_function
import argparse
import os
import re
import subprocess
import urllib2
import errno
import sys

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DOWNLOADS_DIR = os.path.join(SCRIPT_DIR, 'downloads')
SOURCES_DIR = os.path.join(SCRIPT_DIR, 'sources')

class Utils:
    @staticmethod
    def mkdir_p(path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

class Downloader:
    def __init__(self, download_dir):
        self.download_dir = download_dir
        ftp_gnu_org_tpl = 'https://ftp.gnu.org/gnu/%NAME%/%NAME%-%VERSION%.%EXT%'
        xiph_org_tpl = 'http://downloads.xiph.org/releases/%NAME%/lib%NAME%-%VERSION%.%EXT%'
        self.sources = [
            ['binutils', '2.29', 'tar.xz', ftp_gnu_org_tpl],
            ['coreutils', '8.27', 'tar.xz', ftp_gnu_org_tpl],
            ['sed', '4.4', 'tar.xz', ftp_gnu_org_tpl],
            ['gdb', '8.0.1', 'tar.xz', ftp_gnu_org_tpl],
            ['gmp', '6.1.2', 'tar.xz', ftp_gnu_org_tpl],
            ['mpfr', '3.1.5', 'tar.xz', ftp_gnu_org_tpl],
            ['mpc', '1.0.3', 'tar.gz', ftp_gnu_org_tpl],
            ['gcc', '7.2.0', 'tar.xz', 'https://ftp.gnu.org/gnu/gcc/gcc-%VERSION%/gcc-%VERSION%.%EXT%'],
            ['make', '4.2.1', 'tar.bz2', ftp_gnu_org_tpl],
            ['grep', '3.1', 'tar.xz', ftp_gnu_org_tpl],
            ['ogg', '1.3.2', 'tar.xz', xiph_org_tpl],
            ['vorbis', '1.3.5', 'tar.xz', xiph_org_tpl],
            ['boost', '1.65.0', 'zip', 'http://dl.bintray.com/boostorg/release/%VERSION%/source/%NAME%_%MAJOR%_%MINOR%_%PATCH%.%EXT%'],
            ['isl', '0.18', 'tar.xz', 'http://isl.gforge.inria.fr/%NAME%-%VERSION%.%EXT%'],
            ['mingw-w64', '5.0.2', 'tar.bz2', 'https://downloads.sourceforge.net/project/mingw-w64/mingw-w64/mingw-w64-release/mingw-w64-v%VERSION%.%EXT%'],
            ['bzip2', '1.0.6', 'tar.gz', 'http://www.bzip.org/%VERSION%/bzip2-%VERSION%.%EXT%'],
            ['SDL2', '2.0.5', 'tar.gz', 'https://www.libsdl.org/release/SDL2-%VERSION%.%EXT%'],
            ['SDL2_mixer', '2.0.1', 'tar.gz', 'https://www.libsdl.org/projects/SDL_mixer/release/SDL2_mixer-%VERSION%.%EXT%'],
            ['vorbis-tools', '1.4.0', 'tar.gz', 'http://downloads.xiph.org/releases/vorbis/vorbis-tools-%VERSION%.%EXT%'],
            ['zlib', '1.2.11', 'tar.gz', 'https://zlib.net/%NAME%-%VERSION%.%EXT%'],
            ['pngcrush', '1.8.12', 'tar.xz', 'https://downloads.sourceforge.net/project/pmt/pngcrush/%VERSION%/pngcrush-%VERSION%-nolib.%EXT%'],
            ['pngcheck', '2.3.0', 'tar.gz', 'https://downloads.sourceforge.net/project/png-mng/pngcheck/%VERSION%/pngcheck-%VERSION%.%EXT%'],
            ['pcre2', '10.30', 'tar.bz2', 'https://downloads.sourceforge.net/pcre/pcre2-%VERSION%.%EXT%'],
            ['glm', '0.9.8.5', '7z', 'https://github.com/g-truc/glm/releases/download/%VERSION%/glm-%VERSION%.%EXT%'],
            ['freetype', '2.8', 'tar.bz2', 'http://download.savannah.gnu.org/releases/freetype/freetype-%VERSION%.%EXT%'],
            ['glbinding', '2.1.3', 'tar.gz', 'https://github.com/cginternals/glbinding/archive/v%VERSION%.%EXT%'],
            ['libpng', '1.6.32', 'tar.xz', 'https://downloads.sourceforge.net/project/libpng/libpng16/%VERSION%/libpng-%VERSION%.%EXT%'],
            ['lame', '3.99.5', 'tar.gz', 'https://downloads.sourceforge.net/project/lame/lame/%MAJOR%.%MINOR%/lame-%VERSION%.%EXT%'],
        ]

    def download_all(self):
        Utils.mkdir_p(seld.download_dir)
        for source in self.sources:
            self.download_package(source)
    
    def download_package(self, source):
        name = source[0]
        version = source[1]
        ext = source[2]
        url = self.expand_url(source[3], name, version, ext)
        filepath = os.path.join(self.download_dir, name + '-' + version + '.' + ext)
        self.download_file(url, filepath, name)

    def download_file(self, url, filepath, name):
        try:
            src = urllib2.urlopen(url)
            try:
                meta = src.info()
                file_size = int(meta.getheaders("Content-Length")[0])
                if self.is_file_downloaded(filepath, file_size):
                    print("Skipping %s" % (name))
                    return

                print("Downloading: %s Bytes: %s" % (name, file_size))
                with open(filepath, 'wb') as dest:
                    file_size_dl = 0
                    block_sz = 8192
                    while True:
                        buffer = src.read(block_sz)
                        if not buffer:
                            break
                        file_size_dl += len(buffer)
                        dest.write(buffer)
                        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
                        status = status + chr(8)*(len(status)+1)
                        print(status, end='')
            finally:
                src.close()
        except:
            print('cannot load {0} from url {1}'.format(name, url))
            sys.stdout.flush()
            raise

    def is_file_downloaded(self, filepath, file_size):
        if os.path.exists(filepath):
            stats = os.stat(filepath)
            if stats.st_size == file_size:
                return True
        return False

    def expand_url(self, url, name, version, ext):
        version_parts = version.split('.')
        get_part = lambda i: version_parts[i] if len(version_parts) > i else ""
        major = get_part(0)
        minor = get_part(1)
        patch = get_part(2)
        params = {
            '%NAME%': name,
            '%VERSION%': version,
            '%MAJOR%': major,
            '%MINOR%': minor,
            '%PATCH%': patch,
            '%EXT%': ext,
        }
        for key, value in params.iteritems():
            url = url.replace(key, value)
        return url

class Git:
    @staticmethod
    def clone_smart(url, repo_path):
        if not os.path.exists(repo_path):
            subprocess.check_call(['git', 'clone', url, repo_path], cwd=SCRIPT_DIR)

    @staticmethod
    def upgrade(repo_path):
        if not os.path.isabs(repo_path):
            repo_path = os.path.join(SCRIPT_DIR, repo_path)
        subprocess.check_call(['git', 'checkout', 'master'], cwd=repo_path)
        subprocess.check_call(['git', 'pull', 'origin', 'master'], cwd=repo_path)
        subprocess.check_call(['git', 'diff', '--exit-code'], cwd=repo_path)
    pass

class SourceExtractor:
    def __init__(self, src_dir, dest_dir):
        self.src_dir = src_dir
        self.dest_dir = dest_dir

    def extract_all(self):
        for filename in os.listdir(self.src_dir):
            filepath = os.path.join(self.src_dir, filename)
            dest_path = os.path.join(self.dest_dir, os.path.basename(filename))
            self.extract_smart(filepath, dest_path)
    
    def extract_smart(self, filepath, dest_path):
        pass

def download():
    downloader = Downloader(DOWNLOADS_DIR)
    downloader.download_all()
    Git.clone_smart('https://github.com/StephanTLavavej/mingw-distro.git', 'mingw-distro')
    Git.upgrade('mingw-distro')

def prepare():
    extractor = SourceExtractor(DOWNLOADS_DIR, SOURCES_DIR)
    extractor.extract_all()

def build():
    pass

def package():
    pass

def dispatch_tasks():
    parser = argparse.ArgumentParser('Available tasks: all, download, prepare, build, package')
    parser.add_argument('task', type=str, help='all, download, prepare, build or package')
    args = parser.parse_args()
    if args.task == 'all':
        download()
        prepare()
        build()
        package()
    elif args.task == 'download':
        download()
    elif args.task == 'prepare':
        prepare()
    elif args.task == 'build':
        build()
    elif args.task == 'package':
        package()
    else:
        print('nothing to do')

def main():
    try:
        dispatch_tasks()
    except urllib2.HTTPError as error:
        print(str(error))

if __name__ == '__main__':
    main()
