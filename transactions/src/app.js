
const express = require('express');
const { MongoClient, ObjectId } = require('mongodb');

const app = express();
const port = process.env.PORT || 3000;

console.log('Starting transactions service...');

app.use(express.json());

// Request logging
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  next();
});

// MongoDB connection
const mongoUri = process.env.MONGO_URI || 'mongodb://mongo:27017';
const client = new MongoClient(mongoUri);

async function connectToMongo() {
  try {
    console.log('Attempting MongoDB connection...');
    await client.connect();
    await client.db().command({ ping: 1 });
    console.log('Successfully connected to MongoDB!');
  } catch (err) {
    console.error('MongoDB connection failed:', err);
    process.exit(1);
  }
}

connectToMongo();

// Transactions API
app.get('/api/transactions/:userId', async (req, res) => {
  console.log(`Handling transaction request for user: ${req.params.userId}`);

  try {
    const db = client.db('bank_app');

    // Validate user ID
    if (!ObjectId.isValid(req.params.userId)) {
      return res.status(400).json({
        error: 'Invalid user ID format'
      });
    }

    const userId = new ObjectId(req.params.userId);

    // Check if user exists
    const user = await db.collection('users').findOne({
      _id: userId
    });

    if (!user) {
      return res.status(404).json({
        error: 'User not found'
      });
    }

    console.log(
      `Found user with ${user.transactions?.length || 0} transactions`
    );

    // Group transactions by month and year
    const transactions = await db.collection('users').aggregate([
      {
        $match: { _id: userId }
      },
      {
        $unwind: '$transactions'
      },
      {
        $addFields: {
          'transactions.date': {
            $cond: {
              if: {
                $eq: [
                  { $type: '$transactions.date' },
                  'string'
                ]
              },
              then: {
                $toDate: '$transactions.date'
              },
              else: '$transactions.date'
            }
          }
        }
      },
      {
        $group: {
          _id: {
            month: { $month: '$transactions.date' },
            year: { $year: '$transactions.date' }
          },
          transactions: {
            $push: {
              type: '$transactions.type',
              amount: '$transactions.amount',
              date: '$transactions.date'
            }
          }
        }
      },
      {
        $sort: {
          '_id.year': -1,
          '_id.month': -1
        }
      }
    ]).toArray();

    // Format month for dashboard
    const formattedTransactions = transactions.map(group => {
      const monthDate = new Date(
        group._id.year,
        group._id.month - 1,
        1
      );

      return {
        month: monthDate.toLocaleString('en-US', {
          month: 'long',
          year: 'numeric'
        }),
        transactions: group.transactions
      };
    });

    console.log(
      `Returning ${formattedTransactions.length} transaction groups`
    );

    res.json(formattedTransactions);

  } catch (err) {
    console.error('Error processing transactions:', err);

    res.status(500).json({
      error: 'Server Error'
    });
  }
});

// Start transactions microservice
app.listen(port, () => {
  console.log(
    `Transactions service running on http://localhost:${port}`
  );
});
