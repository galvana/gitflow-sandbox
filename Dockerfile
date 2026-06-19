# Minimal stand-in for the fidesplus image: small + fast to build, but exercises
# the same login -> build -> push-by-tag publish path.
FROM alpine:3.20
COPY src/ /app/src/
RUN echo "gitflow sandbox image" > /version.txt
CMD ["cat", "/version.txt"]
