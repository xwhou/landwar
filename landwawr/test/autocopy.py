from os import system
from os import chdir
from os import getcwd

cur_dir = getcwd()

chdir(cur_dir)
system('rm -rf ./landwar')

chdir(cur_dir)
system('mkdir -p ./landwar/ai')
system('cp ../ai/* ./landwar/ai/ -r')
chdir(cur_dir + '/landwar/ai')
system('rm ./landwar/ai/*.pyc')
system('rm ./landwar/ai/__pycache__ -r')

chdir(cur_dir)
system('mkdir -p ./landwar/engine')
system('cp ../engine/* ./landwar/engine/ -r')
chdir(cur_dir + '/landwar/engine')
system('rm ./landwar/engine/*.pyc')
system('rm ./landwar/engine/__pycache__ -r')

chdir(cur_dir)
system('mkdir -p ./landwar/bin')
system('cp ../bin/* ./landwar/bin/ -r')
chdir(cur_dir + '/landwar/bin')
system('rm ./landwar/bin/*.pyc')
system('rm ./landwar/bin/__pycache__ -r')

chdir(cur_dir)
system('mkdir -p ./landwar/Data')
system('cp ../Data/* ./landwar/Data/ -r')
chdir(cur_dir + '/landwar/Data')
system('rm ./landwar/data/*.pyc')
system('rm ./landwar/data/__pycache__ -r')

