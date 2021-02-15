#PyChat auto update script
#Run with "sudo bash update.sh"

mv resources/server/accounts.json ..
mv resources/server/admins.txt ..
mv resources/server/banned.txt ..
mv resources/client/config.json ..

cd ..
sudo rm -rf PyChat
sudo rm -rf pychat
git clone https://github.com/PuffinDev/PyChat.git
cd PyChat

mv ../accounts.json resources/server
mv ../admins.txt resources/server
mv ../banned.txt resources/server 
mv ../config.json resources/client

cd ..
cd PyChat

echo PyChat is now updated!