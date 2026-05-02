import { GraphQLClient, gql } from "graphql-request";

const endpoint = import.meta.env.VITE_API_URL || "http://localhost:8081/graphql";
const client = new GraphQLClient(endpoint);

export async function listRecords(kind) {
  const query = gql`
    query($kind: String!) {
      list(kind: $kind) { id kind payload created_at }
    }
  `;
  const data = await client.request(query, { kind });
  return data.list || [];
}

export async function upsertRecord(kind, payload) {
  const mutation = gql`
    mutation($kind: String!, $payload: String!) {
      upsert(kind: $kind, payload: $payload) {
        id kind payload created_at
      }
    }
  `;
  const data = await client.request(mutation, { kind, payload });
  return data.upsert;
}
