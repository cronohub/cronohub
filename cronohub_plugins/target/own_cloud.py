import owncloud

oc = owncloud.Client('http://domain.tld/owncloud')

oc.login('user', 'password')

oc.mkdir('testdir')

oc.put_file('testdir/remotefile.txt', 'localfile.txt')

link_info = oc.share_file_with_link('testdir/remotefile.txt')

print "Here is your link: " + link_info.get_link()