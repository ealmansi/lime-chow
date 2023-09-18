const serverless = require("serverless-http");

/**
 * 
 */
function renderPage (events) {
  return (`
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Chow</title>
      <style>
        img {
          max-width: 400px;
        }
        h4 {
          margin-bottom: 5px;
        }
        h3 {
          margin-top: 5px;
        }
      </style>
    </head>
    <body>
      ${renderEvents(events)}
    </body>
    </html>
  `);
}

function renderEvents (events) {
  return (`
    <ul>
      ${events.map(renderEvent).join("\n")}
    </ul>
  `);
}

function renderEvent (event) {
  const format = require('date-fns/format');
  const parse = require('date-fns/parse');
  const date = parse(event.date, "dd/MM/yy", new Date());
  const venueMetadata = getVenueMetadata(event.venue);
  return (`
    <li id="${event.id}">
      <h4>
        ${[
          event.date,
          format(date, "EEEE"),
          ...(venueMetadata ? [venueMetadata.name] : []),
          ...(venueMetadata ? [venueMetadata.neighbourhood] : []),
        ].join(" - ")}
      </h4>
      <h3>
        <a href="${event.url}" target="_blank" rel="noreferrer">
          ${event.title}
        </a>
      </h3>
      <img src="${event.thumbnail_url}" alt="${event.title}" />
    </li>
  `);
}

function getVenueMetadata (venue) {
  return {
    ["madame_claude"]: {
      name: "Madame Claude",
      neighbourhood: "Kreuzberg",
    },
    ["schokoladen"]: {
      name: "Schokoladen",
      neighbourhood: "Mitte",
    },
    ["wild_at_heart"]: {
      name: "Wild at Heart",
      neighbourhood: "Kreuzberg",
    },
    ["peppi_guggenheim"]: {
      name: "Peppi Guggenheim",
      neighbourhood: "Neukölln",
    },
    ["loophole"]: {
      name: "Loophole",
      neighbourhood: "Neukölln",
    },
  }[venue];
}

/**
 * 
 */
async function getEvents () {
  const {
    DynamoDBClient,
  } = require("@aws-sdk/client-dynamodb");
  const {
    DynamoDBDocumentClient,
    ScanCommand,
  } = require("@aws-sdk/lib-dynamodb");
  const client = DynamoDBDocumentClient.from(
    new DynamoDBClient(),
  );
  const { Items: events } = await client.send(
    new ScanCommand({
      TableName: "events",
    }),
  );
  return events.sort(compareEvents).filter(isUpcoming);
}

function compareEvents (event1, event2) {
  if (event1.id === event2.id) {
    return 0;
  }
  if (event1.date === event2.date) {
    return event1.id.localeCompare(event2.id);
  }
  const parse = require('date-fns/parse');
  const compareAsc = require('date-fns/compareAsc');
  const date1 = parse(event1.date, "dd/MM/yy", new Date());
  const date2 = parse(event2.date, "dd/MM/yy", new Date());
  return compareAsc(date1, date2);
}

function isUpcoming (event) {
  const parse = require('date-fns/parse');
  const isBefore = require('date-fns/isBefore');
  const startOfDay = require('date-fns/startOfDay')
  const date = parse(event.date, "dd/MM/yy", new Date());
  return !isBefore(startOfDay(date), startOfDay(new Date()));
}

/**
 * 
 */
function buildApp () {
  const express = require("express");
  const app = express();
  app.use(express.json());
  app.get("/", async function (_req, res) {
    const events = await getEvents();
    res.send(renderPage(events));
  });
  app.use((_req, res, _next) => {
    res.sendStatus(404);
  });
  return app;
}

/**
 * 
 */
module.exports.handler = serverless(buildApp());
