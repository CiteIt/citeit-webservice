docker run -p 9000:9000 --name minio1 \
  -e "MINIO_ACCESS_KEY=AKIAIZP3ROBHE6QASCAA" \
  -e "MINIO_SECRET_KEY=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" \
  minio/minio server /data



docker run -p 9000:9000 --name minio1 \
  -e "MINIO_ACCESS_KEY=AKIAIZP3ROBHE6QASCAA" \
  -e "MINIO_SECRET_KEY=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" \
  -v /mnt/data:/data \
  -v /mnt/config:/root/.minio \
  minio/minio server /data




docker run -p 9000:9000 --name minio1 \
  -e "MINIO_ACCESS_KEY=ABCDEFGH123456789" \
  -e "MINIO_SECRET_KEY=alksdfj;2452lkjr;ajtsaljgfslakjfgassgf" \
  minio/minio server /data

docker run -p 9000:9000 --name minio1 \
  -e "MINIO_ACCESS_KEY=ABCDEFGH123456789" \
  -e "MINIO_SECRET_KEY=alksdfj;2452lkjr;ajtsaljgfslakjfgassgf" \
  -v /mnt/data:/data \
  -v /mnt/config:/root/.minio \
  minio/minio server /data






cd aws-sam/citeit-app


sam local start-api

brewsterkahle@coolindian.com

brewsterkahle@archive.org
415-561-6900


sam local start-api -p 80 -d 5858

http://127.0.0.1:80/citeit?url=https://www.citeit.net/



wordpress plugin

WordPress Plugin that requests JSON data files from read.citeit.net and displays the contextual information in hidden divs.

Submits new posts to write.citeit.net if the post contains a blockquote or q tag with a "cite" attribute.



We'll hear reargument this morning in Case 08-205, Citizens United v. The Federal Election Commission.

