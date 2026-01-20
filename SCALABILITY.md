Scalability Notes

Right now, this project is meant for learning and small usage, so it runs as a single Flask application with a simple database setup. However, while building it, I tried to keep the structure flexible so it can be scaled later if needed.

Since authentication is handled using JWT, the API is stateless. This means the application does not store user sessions on the server, and multiple instances of the app can run at the same time behind a load balancer if traffic increases.

For a real production setup, SQLite can be replaced with PostgreSQL, which supports better concurrency and performance. Connection pooling can also be enabled to handle multiple requests more efficiently.

If the number of users grows, a caching system like Redis can be added to reduce repeated database queries, especially for frequently accessed data. Basic rate limiting can also be introduced to prevent abuse and protect login endpoints.

Overall, the project is kept simple for now, but it can be scaled step by step without changing the core design.
