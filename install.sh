pip3 install --upgrade pip
pip3 install -r requirements.txt
sudo usermod -aG `whoami` postgres
# sudo -u postgres createdb $DBNAME
sudo -u postgres createdb $DBNAMEPRIVATE
sudo -u postgres psql -c "CREATE USER $DBUSER with password '$DBPASSWORD';"
# sudo -u postgres psql -c "CREATE USER $DBUSERPRIVATE with password '$DBPASSWORDPRIVATE';"
sudo -u postgres psql -d $DBNAME -c "GRANT ALL PRIVILEGES ON DATABASE $DBNAME TO $DBUSER;"
# sudo -u postgres psql -d $DBNAMEPRIVATE -c "GRANT ALL PRIVILEGES ON DATABASE $DBNAMEPRIVATE TO $DBUSERPRIVATE;"
python3 init_db.py
sudo -u postgres psql -d $DBNAME -c "INSERT INTO maps (city,city_name,filename) VALUES ('spb','Saint-Petersburg','spb.png');"
# sudo -u postgres psql -d $DBNAMEPRIVATE -c "INSERT INTO maps (city,city_name,filename) VALUES ('spb','Saint-Petersburg','spb.png');"

# VSE NADO EBASHIT V COMPOSE YA TOGO ROT EBAL
