from os import system
from os import chdir
from os import getcwd

cur_dir = getcwd()

chdir(cur_dir)
chdir('./landwar/ai/wginterface')
system('python setup.py build -j 32')
system('rm -rf *.py *.pyc *.c')
system('cp ./build/lib.linux-x86_64-3.6/ai/wginterface/* ./')
system('rm -rf build')

chdir(cur_dir)
chdir('./landwar/engine/common')
system('python setup.py build -j 32')
system('rm -rf *.py *.pyc *.c')
system('cp ./build/lib.linux-x86_64-3.6/engine/common/* ./')
system('rm -rf build')

chdir(cur_dir)
chdir('./landwar/engine/verify')
system('python setup.py build -j 32')
system('rm -rf *.py *.pyc *.c')
system('cp ./build/lib.linux-x86_64-3.6/engine/verify/* ./')
system('rm -rf build')


chdir(cur_dir)
chdir('./landwar/engine/wgclock')
system('python setup.py build -j 32')
system('rm -rf *.py *.pyc *.c')
system('cp ./build/lib.linux-x86_64-3.6/engine/wgclock/* ./')
system('rm -rf build')


chdir(cur_dir)
chdir('./landwar/engine/wgconst')
system('python setup.py build -j 32')
system('rm -rf *.py *.pyc *.c')
system('cp ./build/lib.linux-x86_64-3.6/engine/wgconst/* ./')
system('rm -rf build')


chdir(cur_dir)
chdir('./landwar/engine/wgloader')
system('python setup.py build -j 32')
system('rm -rf *.py *.pyc *.c')
system('cp ./build/lib.linux-x86_64-3.6/engine/wgloader/* ./')
system('rm -rf build')

chdir(cur_dir)
chdir('./landwar/engine/wgmap')
system('python setup.py build -j 32')
system('rm -rf *.py *.pyc *.c')
system('cp ./build/lib.linux-x86_64-3.6/engine/wgmap/* ./')
system('rm -rf build')

chdir(cur_dir)
chdir('./landwar/engine/wgmessage')
system('python setup.py build -j 32')
system('rm -rf *.py *.pyc *.c')
system('cp ./build/lib.linux-x86_64-3.6/engine/wgmessage/* ./')
system('rm -rf build')

chdir(cur_dir)
chdir('./landwar/engine/wgoperator')
system('python setup.py build -j 32')
system('rm -rf *.py *.pyc *.c')
system('cp ./build/lib.linux-x86_64-3.6/engine/wgoperator/* ./')
system('rm -rf build')


chdir(cur_dir)
chdir('./landwar/engine/wgstate')
system('python setup.py build -j 32')
system('rm -rf *.py *.pyc *.c')
system('cp ./build/lib.linux-x86_64-3.6/engine/wgstate/* ./')
system('rm -rf build')

chdir(cur_dir)
chdir('./landwar/engine/wgweapon')
system('python setup.py build -j 32')
system('rm -rf *.py *.pyc *.c')
system('cp ./build/lib.linux-x86_64-3.6/engine/wgweapon/* ./')
system('rm -rf build')

chdir(cur_dir)
chdir('./landwar/engine/wgwriter')
system('python setup.py build -j 32')
system('rm -rf *.py *.pyc *.c')
system('cp ./build/lib.linux-x86_64-3.6/engine/wgwriter/* ./')
system('rm -rf build')

chdir(cur_dir)
chdir('./landwar/engine/')
system('python setup.py build -j 32')
system('rm -rf *.py *.pyc *.c')
system('cp ./build/lib.linux-x86_64-3.6/engine/* ./')
system('rm -rf build')

# chdir(cur_dir + '/engine')
# system('python setup.py build')
#
# chdir(cur_dir + '/engine/common')
# system('python setup.py build')
#
# chdir(cur_dir + '/engine/wgclock')
# system('python setup.py build')
#
# chdir(cur_dir + '/engine/wgconst')
# system('python setup.py build')
#
# chdir(cur_dir + '/engine/wgloader')
# system('python setup.py build')
#
# chdir(cur_dir + '/engine/wgmap')
# system('python setup.py build')
#
# chdir(cur_dir + '/engine/wgmessage')
# system('python setup.py build')
#
# chdir(cur_dir + '/engine/wgoperator')
# system('python setup.py build')
#
# chdir(cur_dir + '/engine/wgstate')
# system('python setup.py build')
#
# chdir(cur_dir + '/engine/wgweapon')
# system('python setup.py build')
#
# chdir(cur_dir + '/engine/wgwriter')
# system('python setup.py build')
#
# system('mkdir -p ./land_war')
# system('cp ./ai2 ./land_war/ai -r')
# system('cp ./engine2 ./land_war/engine -r')
# system('cp ./Data ./land_war/Data -r')
# system('rm -rf ./ai2')
# system('rm -rf ./engine2')