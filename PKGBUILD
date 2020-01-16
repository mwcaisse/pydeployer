pkgname=pydeployer
pkgver=0.0.1
pkgrel=1
pkgdesc="Python app for building/deploying .NET applications"
arch=('any')
url="https://github.com/mwcaisse/pydeployer"
license=('MIT')
depends=('python>=3.7.0' 'python-requests>=2.22.0' 'python-urllib3>=1.25.6' "python-yaml>=5.1.2")


source=("$pkgname-$pkgver.tar.gz::https://github.com/mwcaisse/pydeployer/archive/master.tar.gz")
md5sums=('SKIP')

backup=("opt/$pkgname/conf/config.yaml")

package() {

    # Copy the script files
    cd "$pkgname-master"
    mkdir -p "$pkgdir/opt/$pkgname/"
    cp -r *.py "$pkgdir/opt/$pkgname/"

    # Copy the template files
    mkdir -p "$pkgdir/opt/$pkgname/templates/"
    cp -r ./templates/* "$pkgdir/opt/$pkgname/templates/"

    # Create the conf dir and copy over the sample config
    mkdir -p "$pkgdir/opt/$pkgname/conf"
    cp sample_config.yaml "$pkgdir/opt/$pkgname/conf/config.yaml"

    # Mark the script as executable
    chmod a+x "$pkgdir/opt/$pkgname/pydeployer.py"

    # Create the binary symlink
    mkdir -p "$pkgdir/usr/bin"
    ln -s "/opt/$pkgname/pydeployer.py" "$pkgdir/usr/bin/$pkgname"
}
