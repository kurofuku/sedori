FROM		debian:latest

ADD			. /conf/

RUN			\
			# Update to latest
			apt -y update && \
			apt -y upgrade && \
			apt -y install git python3 python3-pip libxml2-dev libxslt1-dev zlib1g-dev python3-requests python3-lxml python3-pandas python3-joblib python3-openpyxl && \
			pip3 install pydrive six==1.15.0

ENTRYPOINT  \
			while true; \
			do \
				git clone https://github.com/kurofuku/sedori.git /sedori/sedori; \
				cp /conf/client_secrets.json /sedori/sedori/; \
				cp /conf/credentials.json /sedori/sedori/; \
				cp /conf/settings.yaml /sedori/sedori/; \
				cd /sedori/sedori/ ; \
				python3 scrape.py; \
				cd /sedori/; \
				rm -rf /sedori/sedori; \
				echo "Go to next loop..."; \
				sleep 86400; \
			done
