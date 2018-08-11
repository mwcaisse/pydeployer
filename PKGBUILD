pkgname=pydeployer
pkgver=0.0.1
pkgrel=1
pkgdesc="Python app for building/deploying .NET applications"
arch=('any')
url="https://github.com/mwcaisse/pydeployer"
license=('MIT')
depends=('python>=3.7.0' 'python-requests>=2.19.1' 
'python-urllib3>=1.23')


source=("$pkgname-$pkgver.tar.gz::https://github.com/mwcaisse/pydeployer/archive/master.tar.gz")
md5sums=('SKIP')

package() {

    cd "$pkgname-master"
    mkdir -p "$pkgdir/opt/$pkgname/"
    cp -r *.py "$pkgdir/opt/$pkgname/"

    chmod a+x "$pkgdir/opt/$pkgname/pydeployer.py"

    mkdir -p "$pkgdir/usr/bin"
    ln -s "/opt/$pkgname/pydeployer.py" "$pkgdir/usr/bin/$pkgname"
}
